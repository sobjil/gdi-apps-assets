# 새벽바라기 까마귀 — 블렌더에서 코드로 만들어 GLB 로 내보낸다.
# 실행: blender -b --python crow.py -- <내보낼 경로.glb>
# 앞쪽 = 블렌더 -Y(glTF 로 나가면 +Z — 믹사모 사람과 같은 쪽). 하늘 높이에 떠 있게 만든다(무리 그리기는 바닥 높이에 놓으므로).
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix

out = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = 30
ALT = 1.7                                   # 나는 높이(m)

def mat(name, rgb, rough=0.45, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m
M_BODY = mat('Feather', (0.025, 0.027, 0.035), 0.38)
M_BEAK = mat('Beak', (0.06, 0.06, 0.07), 0.3)
M_EYE = mat('Eye', (0.55, 0.05, 0.03), 0.2)

bm = bmesh.new()
groups = {}                                   # 꼭짓점 → 뼈 이름
def add(geom_verts, group, m_index):
    for v in geom_verts: groups[v] = group
def faces_of(verts):
    fs = set()
    for v in verts: fs.update(v.link_faces)
    return fs
def ellipsoid(c, r, group, mi, seg=12, ring=8):
    res = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=ring, radius=1.0)
    vs = res['verts']
    for v in vs: v.co = Vector((v.co.x * r[0] + c[0], v.co.y * r[1] + c[1], v.co.z * r[2] + c[2]))
    for f in faces_of(vs): f.material_index = mi
    add(vs, group, mi); return vs
def cone(c, r, depth, group, mi, axis='-Y'):
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r, radius2=0.0, depth=depth)
    vs = res['verts']
    rot = Matrix.Rotation(math.radians(90), 4, 'X')            # 원뿔 축(Z) → -Y 쪽으로
    for v in vs:
        v.co = rot @ v.co; v.co += Vector(c)
    for f in faces_of(vs): f.material_index = mi
    add(vs, group, mi); return vs

# 몸통·머리·부리·꼬리
ellipsoid((0, 0.0, ALT), (0.075, 0.17, 0.07), 'body', 0)
ellipsoid((0, -0.17, ALT + 0.045), (0.055, 0.065, 0.055), 'body', 0)
cone((0, -0.255, ALT + 0.035), 0.022, 0.08, 'body', 1)
for s in (-1, 1): ellipsoid((s * 0.035, -0.205, ALT + 0.065), (0.009, 0.009, 0.009), 'body', 2, 6, 4)
tail = ellipsoid((0, 0.21, ALT - 0.005), (0.06, 0.1, 0.012), 'body', 0, 8, 4)
# 날개 — 어깨에서 바깥으로 길게, 끝으로 갈수록 좁고 깃 끝이 갈라지게(세 갈래)
def wing(sign):
    name = 'wing.L' if sign > 0 else 'wing.R'
    pts = [(0.05, -0.06), (0.24, -0.08), (0.42, -0.03), (0.52, 0.04), (0.47, 0.07), (0.42, 0.05), (0.38, 0.1), (0.31, 0.08), (0.26, 0.12), (0.16, 0.1), (0.05, 0.08)]
    top = [bm.verts.new((sign * x, y, ALT + 0.012)) for x, y in pts]
    bot = [bm.verts.new((sign * x, y, ALT - 0.004)) for x, y in pts]
    if sign < 0: top.reverse(); bot.reverse()
    ft = bm.faces.new(top); fb = bm.faces.new(list(reversed(bot)))
    n = len(top)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((top[i], bot[i], bot[j], top[j]) if sign > 0 else (top[j], bot[j], bot[i], top[i]))
    for v in top + bot: groups[v] = name
wing(1); wing(-1)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

bm.verts.index_update()
me = bpy.data.meshes.new('Crow'); bm.to_mesh(me)
for m in (M_BODY, M_BEAK, M_EYE): me.materials.append(m)
ob = bpy.data.objects.new('Crow', me); sc.collection.objects.link(ob)
for g in ('body', 'wing.L', 'wing.R'): ob.vertex_groups.new(name=g)
order = list(groups.items())
bm.verts.ensure_lookup_table()
for v, g in order:
    ob.vertex_groups[g].add([v.index], 1.0, 'REPLACE')
bm.free()
for p in me.polygons: p.use_smooth = False

# 뼈대 — 몸통 하나, 날개 둘(날개뼈는 바깥쪽으로 — 뼈의 X 축이 앞뒤라 X 축으로 돌리면 위아래로 퍼덕인다)
arm = bpy.data.armatures.new('CrowRig'); rig = bpy.data.objects.new('CrowRig', arm); sc.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
b = arm.edit_bones.new('body'); b.head = (0, 0.15, ALT); b.tail = (0, -0.15, ALT)
for s, n in ((1, 'wing.L'), (-1, 'wing.R')):
    w = arm.edit_bones.new(n); w.head = (s * 0.05, 0, ALT); w.tail = (s * 0.5, 0, ALT); w.roll = 0; w.parent = arm.edit_bones['body']
bpy.ops.object.mode_set(mode='OBJECT')
ob.parent = rig; mod = ob.modifiers.new('Armature', 'ARMATURE'); mod.object = rig

# 동작 — 동작마다 액션 하나를 만들고 NLA 트랙에 넣는다(내보낼 때 트랙 이름 = 동작 이름)
rig.animation_data_create()
for pb in rig.pose.bones: pb.rotation_mode = 'XYZ'
def clip(name, frames, keys):
    act = bpy.data.actions.new(name); rig.animation_data.action = act
    for f, pose in keys:
        for bn, (rot, loc) in pose.items():
            pb = rig.pose.bones[bn]; pb.rotation_euler = rot; pb.location = loc
            pb.keyframe_insert('rotation_euler', frame=f); pb.keyframe_insert('location', frame=f)
    tr = rig.animation_data.nla_tracks.new(); tr.name = name
    st = tr.strips.new(name, 1, act); st.name = name
    rig.animation_data.action = None
Z = (0, 0, 0)
def flap(a, bob):  # a = 날개 각도(도), 위로 +
    r = math.radians(a)
    return {'body': ((0, 0, 0), (0, 0, bob)), 'wing.L': ((-r, 0, 0), Z), 'wing.R': ((r, 0, 0), Z)}   # 오른쪽 뼈는 반대로 놓여 부호가 거꾸로
# 날갯짓 — 위로 55°, 아래로 −45°, 0.5초
clip('Walk', 16, [(1, flap(55, -0.02)), (8, flap(-45, 0.03)), (16, flap(55, -0.02))])
clip('Run', 10, [(1, flap(60, -0.02)), (5, flap(-50, 0.03)), (10, flap(60, -0.02))])
# 활공 — 날개를 편 채 살짝 흔들림
clip('Idle', 30, [(1, flap(8, 0)), (15, flap(14, 0.01)), (30, flap(8, 0))])
# 내리꽂기(공격) — 날개를 접고 고개 숙임
def dive(a, pitch, z):
    r = math.radians(a)
    return {'body': ((math.radians(pitch), 0, 0), (0, 0, z)), 'wing.L': ((-r, 0, 0), Z), 'wing.R': ((r, 0, 0), Z)}
clip('Bite', 12, [(1, dive(20, 0, 0)), (6, dive(70, -25, -0.35)), (12, dive(20, 0, 0))])
# 떨어짐(죽음) — 뒤집히며 바닥으로
clip('Death', 24, [(1, dive(10, 0, 0)), (12, {'body': ((0, math.radians(120), 0), (0, 0, -0.9)), 'wing.L': ((math.radians(-30), 0, 0), Z), 'wing.R': ((math.radians(-40), 0, 0), Z)}),
                   (24, {'body': ((0, math.radians(180), 0), (0, 0, -ALT + 0.05)), 'wing.L': ((0, 0, 0), Z), 'wing.R': ((math.radians(-20), 0, 0), Z)})])

for o in (ob, rig): o.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='NLA_TRACKS', export_apply=False, export_yup=True)
print('CROW_OK', out)
