# 새벽바라기 손에 드는 무기 소품 — 블렌더에서 코드로 만들어 한 GLB 에 무기 id 이름의 물체로 담는다.
# 실행: blender -b --python props.py -- <내보낼 경로.glb>
# 손잡이(쥐는 자리) = 원점. 근접 무기는 블렌더 +Z(glTF +Y)로 뻗고, 총은 총구가 블렌더 -Y(glTF +Z, 앞)로 향한다.
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix

out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def mat(name, rgb, rough=0.6, metal=0.0, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = 4.0
    return m
WOOD = mat('Wood', (0.42, 0.26, 0.13), 0.7)
WOOD_D = mat('WoodDark', (0.26, 0.15, 0.08), 0.7)
METAL = mat('Metal', (0.55, 0.56, 0.58), 0.35, 0.8)
GUN = mat('Gunmetal', (0.07, 0.07, 0.08), 0.4, 0.6)
BLACK = mat('Rubber', (0.03, 0.03, 0.03), 0.9)
RUST = mat('Rust', (0.36, 0.2, 0.12), 0.85, 0.3)
RED = mat('Red', (0.6, 0.04, 0.03), 0.4)
YELLOW = mat('Yellow', (0.85, 0.62, 0.05), 0.5)
LAMP = mat('Lamp', (1.0, 0.95, 0.8), 0.2, 0.0, (1.0, 0.92, 0.7))
BLUE = mat('Spark', (0.3, 0.6, 1.0), 0.2, 0.0, (0.4, 0.7, 1.0))

parts = []
def piece(obj, m):
    obj.data.materials.append(m); parts.append(obj); return obj
def cyl(r1, r2, length, pos, rot=(0, 0, 0), m=METAL, seg=12):
    bpy.ops.mesh.primitive_cone_add(vertices=seg, radius1=r1, radius2=r2, depth=length, location=pos, rotation=rot)
    return piece(bpy.context.active_object, m)
def box(size, pos, rot=(0, 0, 0), m=METAL):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos, rotation=rot)
    o = bpy.context.active_object; o.scale = size; return piece(o, m)
def sphere(r, pos, m=METAL, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=r, location=pos)
    o = bpy.context.active_object; o.scale = scale; return piece(o, m)
def done(name):
    global parts
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts: p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.join()
    o = bpy.context.active_object; o.name = name; o.data.name = name
    # 원점은 이미 손잡이 — 물체 원점을 세계 원점에
    bpy.context.scene.cursor.location = (0, 0, 0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    for poly in o.data.polygons: poly.use_smooth = False
    parts = []
    return o
X90 = (math.radians(90), 0, 0)   # 원기둥(Z축) → Y축

# ── 근접 — 손잡이에서 +Z 로 ─────────────────────────────
# W-01 야구방망이
cyl(0.017, 0.034, 0.84, (0, 0, 0.36), m=WOOD); cyl(0.019, 0.019, 0.16, (0, 0, 0.0), m=BLACK); cyl(0.024, 0.024, 0.015, (0, 0, -0.085), m=WOOD)
done('W-01')
# W-04 삼단봉 — 세 마디
cyl(0.016, 0.016, 0.15, (0, 0, 0), m=BLACK); cyl(0.012, 0.012, 0.17, (0, 0, 0.16), m=GUN); cyl(0.009, 0.009, 0.17, (0, 0, 0.32), m=GUN); sphere(0.013, (0, 0, 0.41), m=GUN)
done('W-04')
# W-13 쇠파이프 — 녹슨 끝
cyl(0.018, 0.018, 0.82, (0, 0, 0.3), m=METAL); cyl(0.022, 0.022, 0.05, (0, 0, 0.71), m=RUST); cyl(0.019, 0.019, 0.12, (0, 0, -0.06), m=RUST)
done('W-13')
# W-15 각목 — 못 몇 개
box((0.07, 0.035, 0.95), (0, 0, 0.37), m=WOOD_D)
for z, x in ((0.62, 0.02), (0.72, -0.015), (0.8, 0.01)): cyl(0.003, 0.003, 0.09, (x, 0, z), rot=X90, m=METAL)
done('W-15')
# W-14 손도끼
cyl(0.014, 0.017, 0.38, (0, 0, 0.1), m=WOOD); box((0.11, 0.02, 0.07), (0.045, 0, 0.27), m=METAL); box((0.02, 0.022, 0.08), (0.1, 0, 0.27), m=METAL)
done('W-14')
# W-02 식칼
box((0.025, 0.02, 0.11), (0, 0, 0), m=BLACK); box((0.04, 0.004, 0.2), (0.007, 0, 0.155), m=METAL)
done('W-02')
# W-25 전기 충격기 — 끝에 푸른 불꽃
box((0.045, 0.03, 0.16), (0, 0, 0.04), m=GUN); cyl(0.004, 0.004, 0.03, (0.012, 0, 0.135), m=METAL); cyl(0.004, 0.004, 0.03, (-0.012, 0, 0.135), m=METAL); sphere(0.008, (0, 0, 0.152), m=BLUE)
done('W-25')
# W-11 작업등 — 손잡이 달린 네모 등
box((0.16, 0.08, 0.11), (0, 0, 0.12), m=YELLOW); box((0.14, 0.006, 0.09), (0, -0.042, 0.12), m=LAMP); box((0.025, 0.025, 0.12), (0, 0, 0.0), m=BLACK)
done('W-11')
# W-05 소화기 — 손잡이가 위에 있고 통이 아래로
cyl(0.065, 0.065, 0.42, (0, 0.02, -0.25), m=RED); sphere(0.065, (0, 0.02, -0.04), m=RED, scale=(1, 1, 0.5)); box((0.03, 0.12, 0.02), (0, -0.02, 0.0), m=BLACK)
cyl(0.009, 0.006, 0.18, (0, -0.1, -0.05), rot=(math.radians(60), 0, 0), m=BLACK)
done('W-05')

# ── 총 — 총구가 -Y(앞), 손잡이가 원점에서 아래로 ────────────────
def grip(m=GUN, tilt=15, h=0.11):
    box((0.028, 0.04, h), (0, 0.01, -h / 2 + 0.01), rot=(math.radians(-tilt), 0, 0), m=m)
# W-06 권총
grip(); box((0.03, 0.2, 0.035), (0, -0.06, 0.035), m=GUN); box((0.012, 0.04, 0.02), (0, -0.01, -0.005), m=GUN)
done('W-06')
# W-19 리볼버 — 원통 탄창
grip(m=WOOD_D, tilt=20); cyl(0.022, 0.022, 0.045, (0, -0.03, 0.035), rot=X90, m=METAL); cyl(0.009, 0.009, 0.17, (0, -0.13, 0.045), rot=X90, m=METAL); box((0.02, 0.05, 0.02), (0, 0.02, 0.04), m=METAL)
done('W-19')
# W-18 기관단총 — 짧은 총열·탄창
grip(); box((0.04, 0.3, 0.06), (0, -0.08, 0.04), m=GUN); box((0.022, 0.035, 0.13), (0, -0.09, -0.04), m=GUN); cyl(0.01, 0.01, 0.1, (0, -0.27, 0.05), rot=X90, m=GUN); box((0.025, 0.14, 0.03), (0, 0.12, 0.03), m=GUN)
done('W-18')
# W-07 산탄총 — 긴 총열·펌프·나무 개머리
grip(m=WOOD); cyl(0.014, 0.014, 0.62, (0, -0.33, 0.055), rot=X90, m=GUN); box((0.04, 0.12, 0.05), (0, -0.25, 0.025), m=WOOD); box((0.045, 0.22, 0.06), (0, -0.03, 0.04), m=GUN)
box((0.04, 0.3, 0.07), (0, 0.22, 0.0), rot=(math.radians(8), 0, 0), m=WOOD)
done('W-07')
# W-08 엽총 — 더 긴 총열·조준경
grip(m=WOOD_D); cyl(0.011, 0.011, 0.72, (0, -0.38, 0.05), rot=X90, m=GUN); box((0.04, 0.5, 0.05), (0, -0.12, 0.025), m=WOOD_D); cyl(0.016, 0.016, 0.2, (0, -0.06, 0.1), rot=X90, m=GUN)
box((0.04, 0.3, 0.07), (0, 0.24, 0.0), rot=(math.radians(8), 0, 0), m=WOOD_D)
done('W-08')
# W-21 네일건 — 뭉툭한 노란 몸통
grip(m=BLACK, tilt=10); box((0.06, 0.24, 0.09), (0, -0.06, 0.05), m=YELLOW); box((0.03, 0.04, 0.03), (0, -0.2, 0.02), m=BLACK); box((0.02, 0.18, 0.03), (0, -0.07, -0.02), m=BLACK)
done('W-21')
# W-17 석궁 — 활대 양쪽으로
grip(m=WOOD_D); box((0.035, 0.5, 0.04), (0, -0.12, 0.03), m=WOOD_D); box((0.5, 0.025, 0.02), (0, -0.34, 0.04), m=GUN); cyl(0.0015, 0.0015, 0.47, (0, -0.25, 0.04), rot=(0, math.radians(90), 0), m=BLACK)
done('W-17')
# W-16 새총 — Y 갈래
box((0.022, 0.022, 0.1), (0, 0, 0), m=WOOD); box((0.018, 0.018, 0.09), (0.03, 0, 0.08), rot=(0, math.radians(-25), 0), m=WOOD); box((0.018, 0.018, 0.09), (-0.03, 0, 0.08), rot=(0, math.radians(25), 0), m=WOOD)
done('W-16')
# W-20 화염방사기 — 관 끝 불씨
grip(m=GUN); cyl(0.022, 0.016, 0.55, (0, -0.25, 0.05), rot=X90, m=METAL); sphere(0.014, (0, -0.53, 0.05), m=mat('Flame', (1, 0.4, 0.05), 0.3, 0, (1, 0.45, 0.1))); cyl(0.045, 0.045, 0.22, (0, 0.12, 0.0), m=RED)
done('W-20')

for o in bpy.data.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=False, export_yup=True, export_apply=True)
print('PROPS_OK', [o.name for o in bpy.data.objects])
