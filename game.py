import json
import math
import os
import random
import sys
import time
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

from ursina import *
from ursina.models.procedural.cone import Cone
from ursina.models.procedural.cylinder import Cylinder


def rgb(r, g, b):
    return color.rgb(r / 255, g / 255, b / 255)


def rgba(r, g, b, a):
    return color.rgba(r / 255, g / 255, b / 255, a / 255)


SMOKE = '--smoke' in sys.argv
SAVE_PATH = Path(__file__).with_name('save.json')

SPECIES = {
    'dragon': {
        'label': 'Dragon',
        'blurb': 'brave and fiery',
        'body': rgb(88, 190, 110),
        'accent': rgb(45, 130, 75),
        'horn': False,
        'names': ['Ember', 'Flint', 'Moss', 'Cinder'],
    },
    'unicorn': {
        'label': 'Unicorn',
        'blurb': 'sparkly and kind',
        'body': rgb(246, 242, 255),
        'accent': rgb(255, 170, 220),
        'horn': True,
        'names': ['Luna', 'Sparkle', 'Willa', 'Starla'],
    },
    'phoenix': {
        'label': 'Phoenix',
        'blurb': 'reborn in flame',
        'body': rgb(255, 145, 60),
        'accent': rgb(235, 80, 40),
        'horn': False,
        'names': ['Blaze', 'Sunny', 'Ash', 'Flicker'],
    },
    'fairy': {
        'label': 'Fairy Cat',
        'blurb': 'curious magic',
        'body': rgb(205, 155, 255),
        'accent': rgb(255, 215, 245),
        'horn': False,
        'names': ['Mochi', 'Pixie', 'Whisker', 'Biscuit'],
    },
}

DEFAULT_STATE = {
    'name': 'Ember',
    'species': None,
    'stars': 0,
    'hunger': 80.0,
    'happy': 85.0,
    'energy': 90.0,
    'level': 1,
    'xp': 0.0,
    'last': 0.0,
}


def load_state():
    state = dict(DEFAULT_STATE)
    try:
        saved = json.loads(SAVE_PATH.read_text(encoding='utf-8'))
        for key in state:
            if key in saved:
                state[key] = saved[key]
        if state['species'] not in SPECIES:
            state['species'] = None
    except Exception:
        pass
    return state


def save_game():
    if not state:
        return
    state['last'] = time.time()
    try:
        SAVE_PATH.write_text(json.dumps(state, indent=2), encoding='utf-8')
    except Exception:
        pass


def apply_offline_decay():
    elapsed = time.time() - float(state.get('last') or time.time())
    minutes = max(0.0, min(elapsed / 60.0, 60.0))
    state['hunger'] = max(0.0, state['hunger'] - 0.15 * minutes)
    state['happy'] = max(0.0, state['happy'] - 0.10 * minutes)
    state['energy'] = min(100.0, state['energy'] + 1.0 * minutes)


state = load_state()
started = False
pet = None
pet_body = None
pet_tail = None
msg_token = 0
last_save = 0.0

app = Ursina(
    title='My Magical Pet World 3D',
    size=(1280, 760),
    fullscreen=False,
    borderless=False,
    development_mode=False,
    editor_ui_enabled=False,
    vsync=True,
)
if hasattr(window, 'fps_counter'):
    window.fps_counter.enabled = False

Sky(color=rgb(78, 118, 205))

grass = rgb(96, 175, 96)
Entity(model=Cylinder(resolution=32), scale=(40, 1, 40), y=-0.5, color=grass)
Entity(model=Cone(resolution=24), scale=(36, 16, 36), y=-8.5, rotation_x=180, color=rgb(122, 86, 62))

tree_tops = [rgb(70, 160, 80), rgb(52, 140, 96), rgb(110, 185, 70)]
for i in range(15):
    ang = random.uniform(0, math.tau)
    rad = random.uniform(7.5, 16)
    x, z = math.cos(ang) * rad, math.sin(ang) * rad
    h = random.uniform(1.3, 2.1)
    Entity(model=Cylinder(resolution=8), scale=(0.5, h, 0.5), position=(x, h / 2, z), color=rgb(98, 66, 46))
    Entity(model='sphere', scale=random.uniform(1.7, 2.5), position=(x, h + 0.9, z), color=random.choice(tree_tops))

for i in range(7):
    ang = random.uniform(0, math.tau)
    rad = random.uniform(4, 15)
    x, z = math.cos(ang) * rad, math.sin(ang) * rad
    crystal = Entity(
        model='diamond',
        scale=random.uniform(0.8, 1.4),
        position=(x, 1.0, z),
        rotation_y=random.uniform(0, 360),
        color=rgb(120, 230, 255),
    )
    PointLight(parent=crystal, y=0.8, color=rgb(80, 200, 255))

for i in range(8):
    ang = random.uniform(0, math.tau)
    rad = random.uniform(3, 15)
    x, z = math.cos(ang) * rad, math.sin(ang) * rad
    Entity(model='sphere', scale=(random.uniform(0.6, 1.3), 0.5, random.uniform(0.6, 1.3)),
           position=(x, 0.2, z), color=rgb(150, 150, 160))

sun = DirectionalLight(shadows=True, color=rgb(255, 242, 225))
sun.rotation = Vec3(50, -35, 0)
AmbientLight(color=rgba(150, 155, 190, 255))


def build_player():
    root = Entity(name='player', position=(0, 0, 0))
    Entity(parent=root, model='cube', scale=(0.55, 0.7, 0.4), y=0.55, color=rgb(122, 82, 205))
    Entity(parent=root, model='sphere', scale=0.5, y=1.15, color=rgb(255, 218, 190))
    Entity(parent=root, model='sphere', scale=(0.07, 0.08, 0.05), position=(-0.11, 1.2, 0.23), color=rgb(35, 30, 45))
    Entity(parent=root, model='sphere', scale=(0.07, 0.08, 0.05), position=(0.11, 1.2, 0.23), color=rgb(35, 30, 45))
    Entity(parent=root, model=Cylinder(resolution=12), scale=(0.85, 0.06, 0.85), y=1.44, color=rgb(70, 55, 175))
    Entity(parent=root, model=Cone(resolution=12), scale=(0.55, 0.65, 0.55), y=1.78, color=rgb(70, 55, 175))
    return root


def build_pet(species_id):
    global pet, pet_body, pet_tail
    if pet is not None:
        destroy(pet)
    sp = SPECIES[species_id]
    pet = Entity(name='pet', position=(2.5, 0.45, 2.5))
    pet_body = Entity(parent=pet, model='sphere', scale=(0.5, 0.4, 0.6), color=sp['body'])
    Entity(parent=pet, model='sphere', scale=0.36, position=(0, 0.28, 0.4), color=sp['body'])
    Entity(parent=pet, model=Cone(resolution=8), scale=(0.12, 0.2, 0.12), position=(-0.14, 0.5, 0.36), color=sp['accent'])
    Entity(parent=pet, model=Cone(resolution=8), scale=(0.12, 0.2, 0.12), position=(0.14, 0.5, 0.36), color=sp['accent'])
    Entity(parent=pet, model='sphere', scale=(0.06, 0.07, 0.04), position=(-0.1, 0.3, 0.72), color=rgb(35, 30, 45))
    Entity(parent=pet, model='sphere', scale=(0.06, 0.07, 0.04), position=(0.1, 0.3, 0.72), color=rgb(35, 30, 45))
    if sp['horn']:
        Entity(parent=pet, model=Cone(resolution=8), scale=(0.08, 0.35, 0.08), position=(0, 0.55, 0.5), color=rgb(255, 214, 96))
    pet_tail = Entity(parent=pet, model='sphere', scale=(0.1, 0.1, 0.22), position=(0, 0.1, -0.5), color=sp['accent'])
    update_pet_scale()
    return pet


def xp_need():
    return 30 + state['level'] * 20


def update_pet_scale():
    if pet is None:
        return
    s = min(1.5, 1 + (state['level'] - 1) * 0.08)
    pet.scale = Vec3(s, s, s)


def gain_xp(amount):
    state['xp'] += amount
    while state['xp'] >= xp_need():
        state['xp'] -= xp_need()
        state['level'] += 1
        state['stars'] += 10
        update_pet_scale()
        show_message('Level up! Now level ' + str(state['level']) + '.  (+10 stars)')


player = build_player()
pet = None

pivot = Entity(position=(0, 1.6, 0))
camera.parent = pivot
camera.position = Vec3(0, 1.6, -7)
camera.look_at(pivot.world_position)
cam_yaw = 45.0
zoom = 7.0
vy = 0.0
moving_now = False
exhausted = False

stars = []
for i in range(16):
    ang = random.uniform(0, math.tau)
    rad = random.uniform(1.5, 15.5)
    pos = Vec3(math.cos(ang) * rad, random.uniform(1.0, 2.6), math.sin(ang) * rad)
    e = Entity(model='sphere', scale=0.45, position=pos, color=rgb(255, 224, 96))
    Entity(parent=e, model='sphere', scale=1.7, color=rgba(255, 224, 120, 55))
    stars.append({'e': e, 'base_y': pos.y, 'phase': random.uniform(0, math.tau),
                  'active': True, 'respawn': 0.0})


def new_star_position():
    ang = random.uniform(0, math.tau)
    rad = random.uniform(1.5, 15.5)
    return Vec3(math.cos(ang) * rad, random.uniform(1.0, 2.6), math.sin(ang) * rad)


fireflies = []
for i in range(12):
    ang = random.uniform(0, math.tau)
    rad = random.uniform(2, 16)
    bx, bz = math.cos(ang) * rad, math.sin(ang) * rad
    e = Entity(model='sphere', scale=0.14, position=(bx, random.uniform(1, 3), bz),
               color=rgb(190, 255, 170))
    fireflies.append({'e': e, 'bx': bx, 'bz': bz, 'phase': random.uniform(0, math.tau),
                      'speed': random.uniform(0.4, 1.1), 'y': e.y})

sun.update_bounds()

hud = Entity(parent=camera.ui, enabled=False)


def make_label(text, pos, col=color.white, size=1.0, parent=hud, origin=(-0.5, 0.5)):
    return Text(parent=parent, text=text, position=pos, color=col, scale=size, origin=origin)


def make_bar(y, col):
    bg = Entity(parent=hud, model='quad', color=rgba(0, 0, 0, 190),
                origin=(-0.5, 0), position=(-0.55, y), scale=(0.42, 0.026))
    return Entity(parent=bg, model='quad', color=col, origin=(-0.5, 0),
                  position=(0, 0), scale=(1, 0.8))


t_title = make_label('My Magical Pet World 3D', (-0.79, 0.465), color.gold, 2.0)
t_pet = make_label('', (-0.79, 0.42), color.white, 1.4)
t_stars = make_label('Stars: 0', (-0.79, 0.375), color.gold, 1.4)
make_label('Hunger', (-0.79, 0.318), rgb(255, 175, 110), 1.15)
make_label('Happiness', (-0.79, 0.263), rgb(255, 150, 215), 1.15)
make_label('Energy', (-0.79, 0.208), rgb(140, 235, 195), 1.15)
make_label('XP', (-0.79, 0.153), rgb(255, 220, 130), 1.15)
bar_hunger = make_bar(0.325, rgb(255, 150, 70))
bar_happy = make_bar(0.27, rgb(240, 110, 200))
bar_energy = make_bar(0.215, rgb(90, 220, 170))
bar_xp = make_bar(0.16, rgb(255, 200, 80))
make_label('WASD move | Q/E camera | Space jump | F feed | P play | Esc quit',
           (-0.79, -0.46), rgb(190, 185, 220), 1.05)
msg_text = Text(parent=camera.ui, text='', origin=(0, 0), position=(0, -0.3), scale=1.5, color=color.gold)

menu = Entity(parent=camera.ui)
Text(parent=menu, text='My Magical Pet World 3D', origin=(0, 0), position=(0, 0.42),
     scale=2.2, color=color.gold)
Text(parent=menu, text='Choose your magical pet', origin=(0, 0), position=(0, 0.33), scale=1.3)
species_buttons = {}
for i, (sid, sp) in enumerate(SPECIES.items()):
    b = Button(parent=menu, text=sp['label'], position=(-0.33 + i * 0.22, 0.17),
               scale=(0.18, 0.12), color=rgba(255, 255, 255, 30))
    species_buttons[sid] = b
name_label = Text(parent=menu, text='Name: ---', origin=(0, 0), position=(0, 0.02), scale=1.3)
shuffle_btn = Button(parent=menu, text='New name', position=(0, -0.08), scale=(0.22, 0.06),
                     color=rgba(255, 255, 255, 45))
start_btn = Button(parent=menu, text='Start Adventure', position=(0, -0.2), scale=(0.3, 0.075),
                   color=rgb(70, 190, 120))
Text(parent=menu, text='WASD move | Q/E camera | Space jump | F feed | P play',
     origin=(0, 0), position=(0, -0.34), scale=1.05, color=rgb(190, 185, 220))
Text(parent=menu, text='Grab stars to earn coins for snacks!',
     origin=(0, 0), position=(0, -0.4), scale=1.05, color=rgb(190, 185, 220))


def show_message(text, dur=3.0):
    global msg_token
    msg_token += 1
    token = msg_token
    msg_text.text = text
    invoke(clear_message, token, delay=dur)


def clear_message(token):
    if token == msg_token:
        msg_text.text = ''


def pet_hop():
    if pet_body is None:
        return
    pet_body.animate_scale(Vec3(1.35, 1.3, 1.35), duration=0.16, curve=curve.out_elastic)
    pet_body.animate_scale(Vec3(1, 1, 1), duration=0.22, delay=0.18)


def feed():
    if state['stars'] < 3:
        show_message('You need 3 stars for a snack. Play Star Catcher by grabbing stars!')
        return
    if state['hunger'] > 95:
        show_message(state['name'] + ' is already full!')
        return
    state['stars'] -= 3
    state['hunger'] = min(100.0, state['hunger'] + 30)
    state['happy'] = min(100.0, state['happy'] + 5)
    gain_xp(6)
    apple = Entity(model='sphere', scale=0.3, color=rgb(230, 60, 60),
                   position=player.position + Vec3(0, 1.3, 0))
    if pet is not None:
        apple.animate_position(pet.position + Vec3(0, 0.7, 0), duration=0.4, curve=curve.in_out_quad)
    invoke(destroy, apple, delay=0.42)
    pet_hop()
    show_message(state['name'] + ' gobbles the snack. Yum!')


def play_with_pet():
    if state['energy'] < 15:
        show_message(state['name'] + ' is too tired. Let them rest!')
        return
    if state['happy'] > 95:
        show_message(state['name'] + ' is already super happy!')
        return
    state['happy'] = min(100.0, state['happy'] + 25)
    state['energy'] = max(0.0, state['energy'] - 15)
    state['hunger'] = max(0.0, state['hunger'] - 6)
    gain_xp(10)
    if pet is not None:
        pet_body.animate_rotation(Vec3(0, 720, 0), duration=0.7, curve=curve.in_out_quad)
    pet_hop()
    show_message(state['name'] + ' spins with joy!')


def jump():
    global vy
    if player.y <= 0.02:
        if state['energy'] < 5:
            show_message('Too tired to jump!')
            return
        state['energy'] = max(0.0, state['energy'] - 5)
        vy = 8.0


def collect_star(star):
    star['active'] = False
    star['e'].animate_scale(0.0, duration=0.15, curve=curve.in_back)
    invoke(respawn_star, star, delay=0.18)
    state['stars'] += 1
    gain_xp(4)


def respawn_star(star):
    star['e'].position = new_star_position()
    star['base_y'] = star['e'].y
    star['e'].scale = 0.45
    star['e'].enabled = True
    star['active'] = True


def update_world(dt):
    now = time.time()
    for star in stars:
        e = star['e']
        if star['active']:
            e.y = star['base_y'] + math.sin(now * 2 + star['phase']) * 0.25
            e.rotation_y = (e.rotation_y + 110 * dt) % 360
            if started:
                dx = e.x - player.x
                dz = e.z - player.z
                if math.hypot(dx, dz) < 1.05 and -1.0 < e.y - player.y < 2.6:
                    collect_star(star)
        elif now >= star['respawn'] and not e.enabled:
            respawn_star(star)
            star['respawn'] = 0.0
    for ff in fireflies:
        e = ff['e']
        t = now * ff['speed'] + ff['phase']
        e.position = (ff['bx'] + math.sin(t) * 2.2, ff['y'] + math.sin(t * 1.7) * 0.7,
                      ff['bz'] + math.cos(t * 0.8) * 2.2)


def update_pet(dt):
    if pet is None:
        return
    now = time.time()
    pet.y = 0.45 + math.sin(now * 4) * 0.09
    back_x = player.x - player.forward.x * 1.5
    back_z = player.z - player.forward.z * 1.5
    dx = back_x - pet.x
    dz = back_z - pet.z
    dist = math.hypot(dx, dz)
    if dist > 7.5:
        pet.x, pet.z = back_x, back_z
    elif dist > 0.35:
        speed = min(6.5, 3.5 + dist)
        step = min(dist, speed * dt)
        pet.x += dx / dist * step
        pet.z += dz / dist * step
        pet.look_at(Vec3(back_x, pet.y, back_z))
    if pet_tail is not None:
        pet_tail.rotation_z = math.sin(now * 6) * 18


def update_hud():
    label = SPECIES[state['species']]['label'] if state['species'] in SPECIES else 'Pet'
    line = state['name'] + ' the ' + label + '   -   Lv ' + str(state['level'])
    if t_pet.text != line:
        t_pet.text = line
    star_line = 'Stars: ' + str(int(state['stars']))
    if t_stars.text != star_line:
        t_stars.text = star_line
    bar_hunger.scale_x = max(0.001, state['hunger'] / 100)
    bar_happy.scale_x = max(0.001, state['happy'] / 100)
    bar_energy.scale_x = max(0.001, state['energy'] / 100)
    bar_xp.scale_x = max(0.001, state['xp'] / xp_need())


def update():
    global cam_yaw, vy, last_save, moving_now, exhausted
    dt = time.dt
    if dt <= 0:
        return
    now = time.time()
    update_world(dt)
    update_pet(dt)

    if not started:
        cam_yaw = (cam_yaw + 9 * dt) % 360
        pivot.rotation_y = cam_yaw
        camera.position = Vec3(0, 1.8, -9)
        camera.look_at(pivot.world_position)
        return

    if held_keys['q']:
        cam_yaw = (cam_yaw + 85 * dt) % 360
    if held_keys['e']:
        cam_yaw = (cam_yaw - 85 * dt) % 360
    pivot.rotation_y = cam_yaw
    target = player.position + Vec3(0, 1.6, 0)
    pivot.position = lerp(pivot.position, target, min(1.0, dt * 6))
    camera.position = Vec3(0, 1.4 + zoom * 0.28, -zoom)
    camera.look_at(pivot.world_position)

    f = camera.forward
    r = camera.right
    fm = math.hypot(f.x, f.z)
    rm = math.hypot(r.x, r.z)
    fx, fz = (f.x / fm, f.z / fm) if fm > 1e-4 else (0, 1)
    rx, rz = (r.x / rm, r.z / rm) if rm > 1e-4 else (1, 0)
    ix = held_keys['d'] - held_keys['a']
    iz = held_keys['w'] - held_keys['s']
    mx = fx * iz + rx * ix
    mz = fz * iz + rz * ix
    mag = math.hypot(mx, mz)
    moving_now = mag > 0.05

    if moving_now:
        mx /= mag
        mz /= mag
        speed = 6.0 if state['energy'] > 0.5 else 3.0
        player.x += mx * speed * dt
        player.z += mz * speed * dt
        player.look_at(Vec3(player.x + mx, player.y, player.z + mz))
        state['energy'] = max(0.0, state['energy'] - 1.1 * dt)
    else:
        state['energy'] = min(100.0, state['energy'] + 4.0 * dt)

    radius = math.hypot(player.x, player.z)
    if radius > 17:
        player.x *= 17 / radius
        player.z *= 17 / radius

    vy -= 25 * dt
    player.y += vy * dt
    if player.y <= 0:
        player.y = 0
        vy = 0

    state['hunger'] = max(0.0, state['hunger'] - 0.10 * dt)
    state['happy'] = max(0.0, state['happy'] - 0.07 * dt)
    if state['hunger'] < 15:
        state['happy'] = max(0.0, state['happy'] - 0.14 * dt)
    if state['energy'] < 0.5 and not exhausted:
        exhausted = True
        show_message(state['name'] + ' is exhausted. Stop moving to rest!')
    elif state['energy'] > 20 and exhausted:
        exhausted = False

    update_hud()

    if now - last_save > 10:
        save_game()
        last_save = now


def input(key):
    global zoom
    if key == 'escape':
        save_game()
        application.quit()
        return
    if not started:
        return
    if key == 'f':
        feed()
    elif key == 'p':
        play_with_pet()
    elif key == 'space':
        jump()
    elif key == 'scroll up':
        zoom = max(4.0, zoom - 1.0)
    elif key == 'scroll down':
        zoom = min(13.0, zoom + 1.0)


def select_species(sid):
    state['species'] = sid
    state['name'] = SPECIES[sid]['names'][0]
    for other_id, btn in species_buttons.items():
        if other_id == sid:
            btn.color = rgb(255, 210, 90)
        else:
            btn.color = rgba(255, 255, 255, 30)
    name_label.text = 'Name: ' + state['name']
    build_pet(sid)


def shuffle_name():
    if state['species'] in SPECIES:
        pool = SPECIES[state['species']]['names']
    else:
        pool = [n for sp in SPECIES.values() for n in sp['names']]
    state['name'] = random.choice(pool)
    name_label.text = 'Name: ' + state['name']


def start_game():
    global started, last_save
    if state['species'] not in SPECIES:
        show_message('Pick a species first!')
        return
    started = True
    hud.enabled = True
    menu.enabled = False
    last_save = time.time()
    save_game()
    show_message('Welcome, ' + state['name'] + '! Grab stars to earn coins.', dur=4)
    if state['hunger'] < 25:
        invoke(show_message, state['name'] + ' is hungry. Press F to feed.', delay=4.5)


for sid, btn in species_buttons.items():
    btn.on_click = Func(select_species, sid)
shuffle_btn.on_click = shuffle_name
start_btn.on_click = start_game


def image_is_black(name):
    try:
        from panda3d.core import PNMImage
        img = PNMImage(name)
        total = 0
        count = 0
        for y in range(0, img.getYSize(), 40):
            for x in range(0, img.getXSize(), 40):
                total += (img.getRed(x, y) + img.getGreen(x, y) + img.getBlue(x, y)) / 3
                count += 1
        return count == 0 or total / count < 0.01
    except Exception:
        return False


def capture(name, attempt=0):
    try:
        result = application.base.screenshot(name, defaultFilename=0)
        if result and (not image_is_black(name) or attempt >= 4):
            print('screenshot:', name, '->', result, 'attempt', attempt)
            return
        if attempt < 4:
            invoke(capture, name, attempt + 1, delay=0.5)
    except Exception as exc:
        print('screenshot failed:', exc)


def smoke_start():
    select_species('unicorn')
    start_game()
    player.x = 5
    player.z = -3


def smoke_shoot():
    capture('smoke_game.png')
    feed()
    play_with_pet()


if SMOKE:
    invoke(capture, 'smoke_menu.png', delay=1.2)
    invoke(smoke_start, delay=1.5)
    invoke(smoke_shoot, delay=3.2)
    invoke(capture, 'smoke_game2.png', delay=4.8)
    invoke(save_game, delay=5.4)
    invoke(application.quit, delay=5.8)
elif state['species'] in SPECIES:
    apply_offline_decay()
    build_pet(state['species'])
    started = True
    hud.enabled = True
    menu.enabled = False
    invoke(show_message, 'Welcome back, ' + state['name'] + '!', delay=0.6)

app.run()
