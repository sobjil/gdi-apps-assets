# 새벽바라기 밤 2-7 지도 모델 — 블렌더에서 코드로 만들어 한 GLB 에 이름 붙은 물체로 담는다(render3d.js 가 이름으로 꺼내 쓴다).
# 실행: blender -b --python map.py -- <내보낼 경로.glb>
# 크기는 실제 미터. 긴 쪽 = 블렌더 X, 정면 = 블렌더 -Y(glTF +Z, 화면 아래쪽 = 카메라 쪽). 바닥 = Z 0, 가운데 = 원점.
# 이름이 「-seg」 로 끝나는 것은 한 칸짜리 — 화면이 긴 건물·선로·난간을 이 칸을 이어 붙여 만든다.
import bpy, math, sys, random

out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(7)

def mat(name, rgb, rough=0.8, metal=0.0, emit=None, es=3.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = es
    return m
CONC = mat('Concrete', (0.42, 0.42, 0.40))
CONC_D = mat('ConcreteDark', (0.24, 0.24, 0.24))
WHITE = mat('WallWhite', (0.70, 0.70, 0.66))
CREAM = mat('Cream', (0.70, 0.60, 0.44))
BRICK = mat('Brick', (0.45, 0.22, 0.16))
GLASS = mat('Glass', (0.05, 0.07, 0.09), 0.15, 0.3)
WIN_LIT = mat('WindowLit', (0.9, 0.75, 0.45), 0.4, 0, (1.0, 0.78, 0.45), 2.5)
METAL = mat('Metal', (0.5, 0.52, 0.55), 0.4, 0.8)
STEEL_D = mat('SteelDark', (0.16, 0.17, 0.19), 0.5, 0.7)
RUST = mat('Rust', (0.4, 0.22, 0.12), 0.85, 0.3)
GREEN = mat('Leaf', (0.12, 0.26, 0.10))
SOIL = mat('Soil', (0.20, 0.14, 0.09), 1.0)
SAND = mat('Sand', (0.38, 0.33, 0.24), 1.0)
RED = mat('Red', (0.62, 0.06, 0.05), 0.5)
YELLOW = mat('Yellow', (0.85, 0.62, 0.06), 0.5)
BLUE = mat('Blue', (0.08, 0.22, 0.55), 0.5)
TEAL = mat('Teal', (0.10, 0.42, 0.40), 0.5)
MINT = mat('Mint', (0.40, 0.58, 0.52), 0.7)
BLACK = mat('Rubber', (0.03, 0.03, 0.03), 0.9)
WOOD = mat('Wood', (0.40, 0.25, 0.13), 0.7)
NET = mat('Net', (0.85, 0.85, 0.85), 0.6)
LAMP = mat('Lamp', (1.0, 0.95, 0.85), 0.2, 0, (1.0, 0.93, 0.8), 6.0)
EXIT = mat('ExitSign', (0.1, 0.8, 0.3), 0.3, 0, (0.2, 1.0, 0.4), 4.0)
BEACON = mat('Beacon', (1.0, 0.1, 0.05), 0.3, 0, (1.0, 0.1, 0.05), 8.0)
GRAVEL = mat('Gravel', (0.22, 0.21, 0.20), 1.0)
TIE = mat('Tie', (0.25, 0.20, 0.16), 0.9)

parts = []
def piece(obj, m):
    obj.data.materials.append(m); parts.append(obj); return obj
def box(size, pos, m=CONC, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos, rotation=rot)
    o = bpy.context.active_object; o.scale = size; return piece(o, m)
def cyl(r, h, pos, m=METAL, rot=(0, 0, 0), seg=10, r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r, radius2=r if r2 is None else r2, depth=h, location=pos, rotation=rot)
    return piece(bpy.context.active_object, m)
def ball(r, pos, m=GREEN, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=pos)
    o = bpy.context.active_object; o.scale = scale; return piece(o, m)
def done(name):
    global parts
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.join()
    o = bpy.context.active_object; o.name = name; o.data.name = name
    bpy.context.scene.cursor.location = (0, 0, 0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    for poly in o.data.polygons: poly.use_smooth = False
    o.location = (0, 0, 0)
    parts = []
    return o
X90 = (math.radians(90), 0, 0); Y90 = (0, math.radians(90), 0)

# ── 밤 2 아파트 단지 ─────────────────────────────────────────
# 아파트 한 칸(폭 8.4m·깊이 7m·8층 21m) — 흰 벽, 층마다 창 두 개·발코니 띠, 정면 1층에 현관 차양
W, Dp, FL, N = 8.4, 7.0, 2.6, 8
box((W, Dp, FL * N), (0, 0, FL * N / 2), m=WHITE)
for f in range(N):
    z = 1.4 + f * FL
    box((W, 0.25, 0.18), (0, -Dp / 2 - 0.12, z - 0.9), m=CONC)                # 층 띠
    box((W, 0.25, 0.18), (0, Dp / 2 + 0.12, z - 0.9), m=CONC)
    for x in (-2.2, 2.2):
        lit = random.random() < 0.18
        box((2.6, 0.12, 1.4), (x, -Dp / 2 - 0.05, z), m=WIN_LIT if lit else GLASS)
        box((2.6, 0.12, 1.4), (x, Dp / 2 + 0.05, z), m=WIN_LIT if random.random() < 0.15 else GLASS)
box((W + 0.3, Dp + 0.3, 0.5), (0, 0, FL * N + 0.25), m=CONC_D)                 # 옥상 턱
box((3.2, 1.6, 0.25), (0, -Dp / 2 - 0.8, 2.8), m=CONC_D)                        # 현관 차양
box((1.8, 0.1, 2.2), (0, -Dp / 2 - 0.02, 1.1), m=GLASS)                          # 현관 유리문
done('apt-seg')
# 화단 5×2m — 낮은 콘크리트 턱에 덤불
box((5, 2, 0.5), (0, 0, 0.25), m=CONC); box((4.7, 1.7, 0.1), (0, 0, 0.5), m=SOIL)
for i in range(5): ball(0.55 + random.random() * 0.2, (-2 + i, random.uniform(-0.3, 0.3), 0.85), scale=(1, 1, 0.8))
done('planter')
# 놀이터 9.4m 사방 — 모래밭 테두리·미끄럼틀·그네 틀·정글짐(겹쳐 다닐 수 있는 곳이라 낮게)
box((9.4, 9.4, 0.06), (0, 0, 0.03), m=SAND)
for s in (-1, 1):
    box((9.4, 0.25, 0.3), (0, s * 4.6, 0.15), m=CONC); box((0.25, 9.4, 0.3), (s * 4.6, 0, 0.15), m=CONC)
box((1.4, 1.4, 0.1), (-2.5, -2, 1.6), m=RED)                                     # 미끄럼틀 발판
for dx in (-0.6, 0.6):
    for dy in (-0.6, 0.6): cyl(0.06, 1.6, (-2.5 + dx, -2 + dy, 0.8), m=YELLOW)
box((0.9, 3.2, 0.08), (-2.5, -0.2, 0.85), m=BLUE, rot=(math.radians(-30), 0, 0))
box((0.2, 1.6, 0.06), (-3.1, -3.2, 0.8), m=YELLOW, rot=(math.radians(-30), 0, 0))  # 사다리
for x in (1.0, 4.0):                                                              # 그네 틀
    cyl(0.07, 2.6, (x, 2.2, 1.1), m=TEAL, rot=(0, math.radians(15 if x > 2 else -15), 0))
box((3.4, 0.12, 0.12), (2.5, 2.2, 2.35), m=TEAL)
for x in (1.8, 3.2):
    cyl(0.015, 1.6, (x, 2.2, 1.55), m=METAL); box((0.5, 0.25, 0.05), (x, 2.2, 0.72), m=BLACK)
for i in range(3):                                                               # 정글짐
    for j in range(3): cyl(0.05, 1.5, (1.8 + i * 0.7, -2.8 + j * 0.7, 0.75), m=RED)
    box((1.5, 0.08, 0.08), (2.5, -2.8 + i * 0.7, 1.5), m=RED); box((0.08, 1.5, 0.08), (1.8 + i * 0.7, -2.1, 1.5), m=RED)
done('playground')
# 경비실 문(3.75×0.75m) — 틀과 철문 두 짝
box((3.75, 0.75, 0.25), (0, 0, 2.55), m=CONC_D)
for s in (-1, 1):
    box((0.25, 0.75, 2.7), (s * 1.75, 0, 1.35), m=CONC_D); box((1.6, 0.12, 2.3), (s * 0.82, 0, 1.15), m=STEEL_D)
done('gate-door')

# ── 밤 3 지하철역 ─────────────────────────────────────────────
# 승강장 기둥 1.5m 사방·3.6m — 타일 기둥에 광고판·위에 보
box((1.5, 1.5, 3.6), (0, 0, 1.8), m=WHITE); box((1.56, 1.56, 0.9), (0, 0, 0.45), m=MINT)
box((1.2, 0.06, 1.6), (0, -0.78, 1.9), m=mat('Ad', (0.3, 0.4, 0.6), 0.4, 0, (0.35, 0.5, 0.75), 1.2))
box((1.7, 1.7, 0.3), (0, 0, 3.75), m=CONC_D)
done('pillar')
# 벤치 4×1.25m — 금속 의자 넷
box((3.8, 0.35, 0.4), (0, 0, 0.2), m=STEEL_D)
for i in range(4): box((0.85, 0.5, 0.06), (-1.45 + i * 0.96, 0, 0.45), m=METAL); box((0.85, 0.06, 0.45), (-1.45 + i * 0.96, 0.24, 0.7), m=METAL)
done('bench')
# 개찰구 3×1.5m — 기계 셋, 사이에 막대
for x in (-1.3, 0, 1.3):
    box((0.35, 1.5, 1.05), (x, 0, 0.525), m=METAL); box((0.36, 0.5, 0.03), (x, -0.35, 1.06), m=mat('Reader', (0.1, 0.4, 0.2), 0.3, 0, (0.2, 0.9, 0.4), 0.7))
for x in (-0.65, 0.65): box((1.0, 0.05, 0.05), (x, 0.1, 0.85), m=RED)
done('turnstile')
# 역무실 창구 3×1.5m
box((3, 1.5, 1.1), (0, 0, 0.55), m=MINT); box((3, 1.5, 0.1), (0, 0, 2.55), m=CONC_D)
box((3, 0.08, 1.4), (0, 0.7, 1.8), m=GLASS)
for x in (-1.45, 1.45): box((0.1, 1.5, 1.5), (x, 0, 1.85), m=METAL)
done('console')
# 선로 한 칸(8m, 폭 2.5m) — 자갈·침목·레일 둘
box((8, 2.5, 0.12), (0, 0, 0.06), m=GRAVEL)
for i in range(10): box((0.25, 2.3, 0.1), (-3.6 + i * 0.8, 0, 0.15), m=TIE)
for y in (-0.72, 0.72): box((8, 0.08, 0.12), (0, y, 0.25), m=METAL)
done('rail-seg')
# 전동차 한 량(20m×3m×3.6m) — 은색 차체·띠·창·문·앞 유리는 앞 칸만(같이 쓴다)
box((20, 3, 3.1), (0, 0, 2.0), m=METAL); box((20, 3.02, 0.25), (0, 0, 2.2), m=mat('Line2', (0.1, 0.55, 0.2), 0.4))
for s in (-1, 1):
    for i in range(6): box((1.6, 0.05, 1.0), (-8 + i * 3.2, s * 1.52, 2.8), m=WIN_LIT)
    for i in range(4): box((1.3, 0.06, 2.0), (-7.2 + i * 4.8, s * 1.52, 1.6), m=STEEL_D)
box((20, 3, 0.4), (0, 0, 0.45), m=STEEL_D)
done('train-car')

# ── 밤 4 학교 ─────────────────────────────────────────────────
# 학교 한 칸(폭 8m·깊이 7.5m·4층 14m) — 크림색 벽·창 줄·위에 낮은 난간
W, Dp, FL, N = 8.0, 7.5, 3.4, 4
box((W, Dp, FL * N), (0, 0, FL * N / 2), m=CREAM)
for f in range(N):
    z = 1.7 + f * FL
    for s in (-1, 1):
        box((W, 0.2, 0.2), (0, s * (Dp / 2 + 0.08), z - 1.2), m=WHITE)
        for x in (-2.6, 0, 2.6): box((2.2, 0.12, 1.6), (x, s * (Dp / 2 + 0.03), z + 0.1), m=WIN_LIT if random.random() < 0.08 else GLASS)
box((W + 0.2, Dp + 0.2, 0.6), (0, 0, FL * N + 0.3), m=WHITE)
done('school-seg')
# 스탠드 한 칸(폭 8m·깊이 5m) — 계단식 콘크리트에 파란 의자 줄
for i in range(5):
    box((8, 5 - i, 0.55), (0, (i) / 2, 0.275 + i * 0.55), m=CONC)
    for x in range(8): box((0.45, 0.4, 0.3), (-3.5 + x, -2.0 + i + 0.2, 0.7 + i * 0.55), m=BLUE)
done('stand-seg')
# 축구 골대 6.25×1.25m — 흰 틀·뒤 그물 막대
for x in (-3.0, 3.0): cyl(0.07, 2.4, (x, -0.5, 1.2), m=NET)
cyl(0.07, 6.1, (0, -0.5, 2.4), m=NET, rot=Y90)
for x in (-3.0, 3.0): box((0.05, 1.3, 0.05), (x, 0.1, 2.4), m=NET, rot=(math.radians(-30), 0, 0))
box((6.0, 0.05, 0.05), (0, 0.55, 0.05), m=NET)
for i in range(13): box((0.02, 0.02, 2.4), (-3 + i * 0.5, 0.25, 1.2), m=NET, rot=(math.radians(15), 0, 0))
done('goalpost')
# 운동장 확성기 — 기둥 4m 에 나팔 둘
cyl(0.12, 4.2, (0, 0, 2.1), m=STEEL_D)
for a in (-30, 30): cyl(0.35, 0.8, (math.sin(math.radians(a)) * 0.3, -0.45, 3.8), m=WHITE, rot=(math.radians(-80), 0, math.radians(a)), r2=0.08, seg=12)
done('speaker')
# 조명탑 14m — 위에 등 여섯
cyl(0.3, 14, (0, 0, 7), m=STEEL_D, r2=0.18)
box((3.2, 0.4, 2.0), (0, -0.3, 14.2), m=STEEL_D)
for i in range(3):
    for j in range(2): box((0.8, 0.1, 0.7), (-1.05 + i * 1.05, -0.52, 13.7 + j * 0.9), m=LAMP)
done('floodlight')

# ── 밤 5 병원 ─────────────────────────────────────────────────
# 병상 3×1.5m — 침대 틀·매트리스·베개·난간·링거대
box((2.9, 1.3, 0.12), (0, 0, 0.62), m=METAL); box((2.7, 1.2, 0.2), (0, 0, 0.78), m=mat('Sheet', (0.72, 0.76, 0.78)))
box((0.6, 0.9, 0.15), (-1.1, 0, 0.95), m=WHITE)
for x in (-1.4, 1.4):
    for y in (-0.6, 0.6): cyl(0.04, 0.6, (x, y, 0.3), m=METAL)
    box((0.08, 1.35, 0.6), (x, 0, 0.95), m=METAL)
for s in (-1, 1): box((1.4, 0.04, 0.3), (0.2, s * 0.68, 1.0), m=METAL)
cyl(0.025, 2.0, (-1.4, -0.85, 1.0), m=METAL); box((0.15, 0.08, 0.25), (-1.4, -0.85, 1.9), m=mat('IV', (0.7, 0.85, 0.9), 0.2))
done('bed')
# 병원 문 6.25×0.75m — 문틀·유리 여닫이 두 짝·밀대
box((6.25, 0.75, 0.4), (0, 0, 2.6), m=WHITE)
for s in (-1, 1):
    box((0.4, 0.75, 2.8), (s * 2.9, 0, 1.4), m=WHITE)
    box((2.6, 0.1, 2.3), (s * 1.35, 0, 1.2), m=GLASS); box((2.2, 0.15, 0.08), (s * 1.35, -0.06, 1.1), m=METAL)
    box((0.3, 0.1, 0.3), (s * 1.35, -0.06, 1.7), m=mat('Plus', (0.8, 0.1, 0.1)))
done('door-h')
# 비상구 등 — 벽에 다는 초록 표시
box((0.9, 0.12, 0.35), (0, 0, 0), m=EXIT)
done('exit-sign')

# ── 밤 6 강 다리 ──────────────────────────────────────────────
# 시내버스 11×2.5×3.2m — 초록 몸통·창 띠·바퀴
box((11, 2.5, 2.7), (0, 0, 1.75), m=mat('Bus', (0.10, 0.45, 0.25), 0.5))
for s in (-1, 1): box((10.2, 0.05, 1.0), (0.2, s * 1.26, 2.3), m=GLASS)
box((0.05, 2.2, 1.4), (-5.51, 0, 2.2), m=GLASS); box((11, 2.52, 0.3), (0, 0, 3.1), m=WHITE)
for x in (-3.6, 3.4):
    for s in (-1, 1): cyl(0.5, 0.35, (x, s * 1.1, 0.5), m=BLACK, rot=X90, seg=14)
done('bus')
# 중앙 분리대(콘크리트) 5×1m
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.45)); o = bpy.context.active_object; o.scale = (5, 0.6, 0.9); piece(o, CONC)
box((5, 1.0, 0.25), (0, 0, 0.12), m=CONC); box((5, 0.62, 0.1), (0, 0, 0.6), m=YELLOW)
done('jersey')
# 다리 난간 한 칸(8m) — 콘크리트 턱·쇠 난간·가로등 받침 없음
box((8, 0.6, 1.0), (0, 0, 0.5), m=CONC)
box((8, 0.08, 0.08), (0, 0, 1.6), m=METAL)
for i in range(5): box((0.08, 0.08, 0.6), (-3.6 + i * 1.8, 0, 1.3), m=METAL)
done('rail-bridge-seg')
# 교각 — 다리 아래 물 위로 선 기둥(깊이 4m)
box((3, 6, 12), (0, 0, -6), m=CONC_D)
done('pier')

# ── 밤 7 방송국 옥상 ──────────────────────────────────────────
# 송신탑 3.75m 사방·높이 24m — 네 다리 격자·꼭대기 붉은 등
for sx in (-1, 1):
    for sy in (-1, 1):
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.12, radius2=0.08, depth=24.4, location=(sx * 0.9, sy * 0.9, 12),
                                        rotation=(-sy * math.atan(0.9 / 24), sx * math.atan(0.9 / 24), 0))
        piece(bpy.context.active_object, RED if False else mat('TowerRW', (0.65, 0.18, 0.12), 0.6) if sx * sy > 0 else WHITE)
for k in range(8):
    z = 1.5 + k * 2.8; e = 1.8 - z / 24 * 0.9
    for s in (-1, 1):
        box((e * 2, 0.06, 0.06), (0, s * e, z), m=STEEL_D); box((0.06, e * 2, 0.06), (s * e, 0, z), m=STEEL_D)
        box((0.05, 0.05, 3.3), (0, s * e, z + 1.4), m=STEEL_D, rot=(0, math.radians(35), 0))
box((3.8, 3.8, 0.5), (0, 0, 0.25), m=CONC_D)
for z in (8, 15): cyl(0.7, 0.3, (1.0, -1.0, z), m=WHITE, rot=(math.radians(70), 0, math.radians(30)), seg=16)
ball(0.35, (0, 0, 24.6), m=BEACON)
done('tower')
# 실외기 4×3×1.6m — 회색 상자·위에 큰 팬 둘
box((4, 3, 1.4), (0, 0, 0.7), m=WHITE); box((4.1, 3.1, 0.12), (0, 0, 1.42), m=CONC_D)
for x in (-1, 1): cyl(0.9, 0.08, (x, 0, 1.5), m=STEEL_D, seg=16); box((1.6, 0.12, 0.05), (x, 0, 1.56), m=METAL); box((0.12, 1.6, 0.05), (x, 0, 1.56), m=METAL)
for i in range(10): box((3.6, 0.03, 0.06), (0, -1.52, 0.2 + i * 0.12), m=CONC_D)
done('hvac')
# 안테나 기둥 6m — 접시 하나·가로대
cyl(0.08, 6, (0, 0, 3), m=METAL); box((1.6, 0.05, 0.05), (0, 0, 4.8), m=METAL)
cyl(0.55, 0.12, (0.3, -0.3, 3.6), m=WHITE, rot=(math.radians(70), 0, math.radians(20)), seg=16, r2=0.3)
cyl(0.25, 0.3, (0, 0, 0.15), m=CONC_D)
ball(0.1, (0, 0, 6.05), m=BEACON)
done('antenna')
# 옥상 난간 한 칸(8m) — 낮은 턱
box((8, 0.5, 1.1), (0, 0, 0.55), m=CONC); box((8, 0.6, 0.12), (0, 0, 1.12), m=CONC_D)
done('parapet-seg')

# ── 공용 — 불타는 차 잔해(차량 좀비가 부서진 자리) ────────────
box((4.2, 1.9, 0.6), (0, 0, 0.55), m=mat('Burnt', (0.08, 0.07, 0.06), 0.95)); box((2.2, 1.7, 0.7), (-0.2, 0, 1.2), m=mat('Burnt2', (0.12, 0.09, 0.07), 0.95))
for x in (-1.4, 1.4):
    for s in (-1, 1): cyl(0.36, 0.25, (x, s * 0.9, 0.36), m=BLACK, rot=X90, seg=10)
box((1.2, 1.4, 0.05), (0.6, 0, 1.56), m=RUST)
done('wreck')

for o in bpy.data.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=False, export_yup=True, export_apply=True)
print('MAP_OK', len(bpy.data.objects), sorted(o.name for o in bpy.data.objects))
