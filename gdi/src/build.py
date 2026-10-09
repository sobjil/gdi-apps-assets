# 과제 지옥 2 3D 모델 — 블렌더로 짓는다(헤드리스):
#   blender -b -P build.py -- <Kenney Furniture Kit GLTF 폴더> <출력 폴더>
# 산출: office.glb(가구 — Kenney 가구 + 직접 지은 파티션·복합기·정수기·결재함·엘리베이터)
#       enemies.glb(업무 22종 — 서류 괴물, 부위별 이름: body·legL·legR·armL·armR·wingL·wingR)
#       props.glb(인력 소품·발사체)
# 앞 = 블렌더 -Y (glTF +Z). 바닥 = z 0. 크기 단위 = 칸(1m).
import bpy, sys, os, math
argv = sys.argv[sys.argv.index('--') + 1:]
FURN_DIR, OUT = argv[0], argv[1]
os.makedirs(OUT, exist_ok=True)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

MATS = {}
def mat(col, rough=0.6, emit=0.0, metal=0.0):
    key = (col, rough, emit, metal)
    if key in MATS: return MATS[key]
    m = bpy.data.materials.new('m_%s' % col.strip('#'))
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    r, g, bl = (int(col[i:i + 2], 16) / 255 for i in (1, 3, 5))
    b.inputs['Base Color'].default_value = (r ** 2.2, g ** 2.2, bl ** 2.2, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (r ** 2.2, g ** 2.2, bl ** 2.2, 1)
        b.inputs['Emission Strength'].default_value = emit
    MATS[key] = m
    return m

def _finish(o, col, bevel=0.0, **mk):
    if bevel:
        md = o.modifiers.new('b', 'BEVEL'); md.width = bevel; md.segments = 2; md.limit_method = 'ANGLE'
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier='b')
    o.data.materials.append(mat(col, **mk))
    bpy.ops.object.shade_smooth() if False else None
    return o

def box(size, loc, col, bevel=0.02, rot=(0, 0, 0), **mk):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = size
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    return _finish(o, col, bevel, **mk)

def cyl(r, h, loc, col, rot=(0, 0, 0), v=16, bevel=0.0, r2=None, **mk):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=v)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=h, location=loc, rotation=rot, vertices=v)
    o = bpy.context.object
    bpy.ops.object.transform_apply(rotation=True)
    return _finish(o, col, bevel, **mk)

def sph(r, loc, col, scale=(1, 1, 1), seg=14, **mk):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=max(6, seg // 2))
    o = bpy.context.object; o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(mat(col, **mk))
    return o

def torus(R, r, loc, col, rot=(0, 0, 0), **mk):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=24, minor_segments=8)
    o = bpy.context.object
    bpy.ops.object.transform_apply(rotation=True)
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(mat(col, **mk))
    return o

def join(objs, name):
    objs = [o for o in objs if o]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1: bpy.ops.object.join()
    o = bpy.context.object; o.name = name; o.data.name = name
    return o

def group(name, parts, coll):
    """parts = {부위이름: [오브젝트…]} → 부위마다 하나로 합쳐 빈 뿌리 아래에 둔다(부위 원점 = 관절 자리)"""
    bpy.ops.object.empty_add(location=(0, 0, 0)); root = bpy.context.object; root.name = name
    for pname, (objs, pivot) in parts.items():
        o = join(objs, f'{name}.{pname}')
        if pivot:   # 관절: 원점을 옮기고 메시는 제자리
            bpy.context.scene.cursor.location = pivot
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        o.parent = root
    for o in [root] + list(root.children):
        for c in o.users_collection: c.objects.unlink(o)
        coll.objects.link(o)
    bpy.context.scene.cursor.location = (0, 0, 0)
    return root

def eyes(z, y, sep=0.09, r=0.065, angry=0.0, col='#ffffff', pupil='#1d1d26', brow='#2a2230'):
    out = []
    for s in (-1, 1):
        out.append(sph(r, (s * sep, y, z), col, scale=(1, 0.6, 1), rough=0.3))
        out.append(sph(r * 0.55, (s * sep + s * 0.005, y - r * 0.45, z - r * 0.1), pupil, scale=(1, 0.6, 1), rough=0.2))
        if angry:
            out.append(box((r * 2.1, 0.02, r * 0.45), (s * sep, y - 0.01, z + r * 1.25), brow, bevel=0.0, rot=(0, s * angry, 0)))
    return out

def mouth(z, y, w=0.08, col='#3a1f28'):
    return box((w, 0.015, 0.022), (0, y, z), col, bevel=0.0)

def legs(x=0.11, h=0.18, col='#2b2d3a', shoe='#1b1c24'):
    L = [cyl(0.035, h, (-x, 0, h / 2 + 0.03), col), box((0.09, 0.13, 0.05), (-x, -0.03, 0.025), shoe, bevel=0.015)]
    R = [cyl(0.035, h, (x, 0, h / 2 + 0.03), col), box((0.09, 0.13, 0.05), (x, -0.03, 0.025), shoe, bevel=0.015)]
    return {'legL': (L, (-x, 0, h + 0.03)), 'legR': (R, (x, 0, h + 0.03))}

def arms(x, z, ln=0.18, col='#2b2d3a', hand='#f2d0b4'):
    out = {}
    for nm, s in (('armL', -1), ('armR', 1)):
        out[nm] = ([cyl(0.028, ln, (s * (x + ln / 2), 0, z), col, rot=(0, math.pi / 2, 0)), sph(0.045, (s * (x + ln), 0, z), hand)], (s * x, 0, z))
    return out

def wings(x, z, col='#e8f2ff'):
    out = {}
    for nm, s in (('wingL', -1), ('wingR', 1)):
        w = box((0.28, 0.05, 0.16), (s * (x + 0.14), 0.02, z), col, bevel=0.03, rot=(0, s * 0.25, 0))
        out[nm] = ([w], (s * x, 0.02, z))
    return out

# ════════════════════════════════════════════════════════════
# 1) 업무(적)
# ════════════════════════════════════════════════════════════
reset()
EN = bpy.data.collections.new('enemies'); bpy.context.scene.collection.children.link(EN)
LH = 0.21   # 다리 높이(몸 바닥)

def sheet_lines(x0, z0, w, n, y, col='#9aa3b5', gap=0.06):
    return [box((w * (0.6 if k == n - 1 else 1), 0.012, 0.018), (x0 + (w * 0.2 if k == n - 1 else 0), y, z0 - k * gap), col, bevel=0) for k in range(n)]

# 기안문 — 흰 A4 한 장
b = [box((0.46, 0.05, 0.62), (0, 0, LH + 0.31), '#fbfbf7', bevel=0.012), box((0.12, 0.052, 0.12), (0.17, 0.0, LH + 0.56), '#e5e5dc', bevel=0)]
b += sheet_lines(0, LH + 0.2, 0.32, 3, -0.03) + eyes(LH + 0.44, -0.035, angry=0.25) + [mouth(LH + 0.36, -0.03)]
group('e_draft', {'body': (b, None), **legs(), **arms(0.23, LH + 0.3)}, EN)
# 전화 — 빨간 탁상 전화기(경북도 대응·전화 민원)
b = [box((0.5, 0.38, 0.26), (0, 0, LH + 0.13), '#d6453d', bevel=0.06), box((0.34, 0.2, 0.06), (0, -0.02, LH + 0.29), '#b8322b', bevel=0.02),
     cyl(0.06, 0.48, (0, 0.02, LH + 0.4), '#2b2b33', rot=(0, math.pi / 2, 0), bevel=0.0), sph(0.08, (-0.24, 0.02, LH + 0.38), '#2b2b33', scale=(1, 1, 0.7)), sph(0.08, (0.24, 0.02, LH + 0.38), '#2b2b33', scale=(1, 1, 0.7))]
b += [cyl(0.018, 0.012, (dx * 0.07, -0.192, LH + 0.12 + dz * 0.06), '#f4f0e6', rot=(math.pi / 2, 0, 0), v=8) for dx in (-1, 0, 1) for dz in (0, -1)]
b += eyes(LH + 0.2, -0.19, sep=0.12, angry=0.3)
group('e_phone', {'body': (b, None), **legs(), **arms(0.25, LH + 0.15)}, EN)
# 메신저 알림 — 노란 말풍선 + 날개
b = [sph(0.2, (0, 0, 0.62), '#ffd23f', scale=(1.15, 0.6, 0.9)), cyl(0.07, 0.14, (-0.1, 0, 0.44), '#ffd23f', rot=(0, 0.6, 0), r2=0.0, v=8),
     box((0.04, 0.03, 0.12), (0, -0.115, 0.67), '#c0392b', bevel=0.01), sph(0.024, (0, -0.115, 0.56), '#c0392b')] + eyes(0.66, -0.11, sep=0.1, r=0.045)
group('e_ping', {'body': (b, None), **wings(0.2, 0.64, '#fff6c8')}, EN)
# 이메일 — 흰 봉투 + 날개
b = [box((0.5, 0.06, 0.34), (0, 0, 0.62), '#f5f7fb', bevel=0.015), box((0.36, 0.05, 0.36), (0, -0.012, 0.69), '#dde3ee', bevel=0.0, rot=(0, math.pi / 4, 0)),
     box((0.5, 0.062, 0.18), (0, 0.001, 0.53), '#f5f7fb', bevel=0.0), cyl(0.05, 0.02, (0, -0.045, 0.62), '#c0392b', rot=(math.pi / 2, 0, 0))] + eyes(0.63, -0.05, sep=0.13, r=0.05, angry=0.2)
group('e_email', {'body': (b, None), **wings(0.25, 0.64)}, EN)
# 폭탄 메일 — 붉은 봉투 + 심지
b = [box((0.5, 0.06, 0.34), (0, 0, 0.62), '#e2574c', bevel=0.015), box((0.36, 0.05, 0.36), (0, -0.012, 0.69), '#c2433a', bevel=0.0, rot=(0, math.pi / 4, 0)),
     box((0.5, 0.062, 0.18), (0, 0.001, 0.53), '#e2574c', bevel=0.0), cyl(0.012, 0.2, (0.18, 0, 0.88), '#5a4636', rot=(0, 0.4, 0)), sph(0.04, (0.22, 0, 0.98), '#ffb02e', emit=4.0)] + eyes(0.63, -0.05, sep=0.13, r=0.05, angry=0.35)
group('e_bomb', {'body': (b, None), **wings(0.25, 0.64, '#ffd7d2')}, EN)
# 업무 지시 — 클립보드
b = [box((0.48, 0.05, 0.64), (0, 0, LH + 0.32), '#a0703c', bevel=0.02), box((0.4, 0.052, 0.52), (0, -0.004, LH + 0.28), '#fbfbf7', bevel=0.0),
     box((0.2, 0.08, 0.08), (0, -0.01, LH + 0.63), '#9aa0aa', bevel=0.02, metal=0.6, rough=0.3)] + sheet_lines(0, LH + 0.36, 0.3, 4, -0.034, col='#4a78c8') + eyes(LH + 0.47, -0.04, angry=0.4)
group('e_order', {'body': (b, None), **legs(), **arms(0.24, LH + 0.32)}, EN)
# 제안서 — 두꺼운 파란 바인더
b = [box((0.5, 0.26, 0.6), (0, 0, LH + 0.3), '#2f6fd6', bevel=0.03), box((0.05, 0.27, 0.6), (-0.25, 0, LH + 0.3), '#2457ad', bevel=0.02),
     box((0.38, 0.262, 0.54), (0.04, 0, LH + 0.3), '#fbfbf7', bevel=0.0), box((0.3, 0.02, 0.1), (0.02, -0.135, LH + 0.48), '#ffffff', bevel=0.005)] + eyes(LH + 0.36, -0.135, angry=0.35)
group('e_binder', {'body': (b, None), **legs(x=0.13), **arms(0.26, LH + 0.3)}, EN)
# 수시 과제 — 노란 포스트잇
b = [box((0.44, 0.04, 0.44), (0, 0, LH + 0.24), '#ffe066', bevel=0.01, rot=(0.12, 0, 0.05)), box((0.44, 0.03, 0.1), (0, 0.03, LH + 0.48), '#f2cf45', bevel=0.0, rot=(0.6, 0, 0.05))]
b += sheet_lines(0, LH + 0.26, 0.3, 2, -0.03, col='#d06c2b') + eyes(LH + 0.34, -0.04, sep=0.1, angry=0.15)
group('e_sticky', {'body': (b, None), **legs(h=0.16), **arms(0.22, LH + 0.24, ln=0.14)}, EN)
# 정책 과제 — 서류가 삐져나온 마닐라 폴더
b = [box((0.54, 0.08, 0.5), (0, 0, LH + 0.25), '#e8c27a', bevel=0.02), box((0.2, 0.08, 0.06), (-0.14, 0, LH + 0.52), '#e8c27a', bevel=0.01),
     box((0.46, 0.03, 0.46), (0.04, 0.03, LH + 0.33), '#fbfbf7', bevel=0.0, rot=(0, -0.08, 0)), box((0.46, 0.03, 0.46), (-0.02, 0.05, LH + 0.36), '#f0f0ea', bevel=0.0, rot=(0, 0.1, 0))] + eyes(LH + 0.3, -0.045, angry=0.45) + [mouth(LH + 0.21, -0.045)]
group('e_folder', {'body': (b, None), **legs(), **arms(0.27, LH + 0.28)}, EN)
# 갑질 — 넥타이 맨 서류가방
b = [box((0.62, 0.3, 0.46), (0, 0, LH + 0.25), '#5b3a26', bevel=0.05), box((0.2, 0.1, 0.1), (0, 0, LH + 0.52), '#3c2618', bevel=0.03),
     box((0.6, 0.31, 0.04), (0, 0, LH + 0.34), '#3c2618', bevel=0.0), box((0.06, 0.31, 0.08), (0, 0, LH + 0.34), '#d4af37', bevel=0.01, metal=0.8, rough=0.3),
     box((0.1, 0.02, 0.24), (0, -0.16, LH + 0.13), '#c0392b', bevel=0.01), box((0.1, 0.03, 0.06), (0, -0.16, LH + 0.27), '#a93226', bevel=0.01)] + eyes(LH + 0.4, -0.155, sep=0.13, r=0.06, angry=0.55)
group('e_boss_small', {'body': (b, None), **legs(x=0.15, h=0.2), **arms(0.32, LH + 0.25, ln=0.22, col='#3c2618')}, EN)
# 수정 요청 — 빨간 펜
b = [cyl(0.11, 0.62, (0, 0, LH + 0.33), '#d63a3a', v=12), cyl(0.11, 0.16, (0, 0, LH + 0.72), '#f2f2f2', v=12), cyl(0.11, 0.12, (0, 0, LH - 0.04 + 0.06), '#f2f2f2', v=12, r2=0.03),
     box((0.03, 0.05, 0.28), (0.1, -0.08, LH + 0.6), '#bdc3c7', bevel=0.005, metal=0.7, rough=0.3)] + eyes(LH + 0.48, -0.1, sep=0.055, r=0.045, angry=0.4)
group('e_redpen', {'body': (b, None), **legs(x=0.07, h=0.16), **arms(0.11, LH + 0.36, ln=0.14)}, EN)
# 야근 유발 — 김 나는 검은 머그
b = [cyl(0.2, 0.42, (0, 0, LH + 0.22), '#2c2a3a', v=20, bevel=0.0), cyl(0.18, 0.02, (0, 0, LH + 0.43), '#4a2a1a', v=20), torus(0.1, 0.03, (0.23, 0, LH + 0.24), '#2c2a3a', rot=(math.pi / 2, 0, 0)),
     sph(0.07, (-0.04, 0, LH + 0.58), '#cfd6e6', rough=0.9), sph(0.05, (0.05, 0, LH + 0.66), '#cfd6e6', rough=0.9), box((0.14, 0.02, 0.1), (0, -0.2, LH + 0.18), '#f5e663', bevel=0.0)] + eyes(LH + 0.32, -0.19, sep=0.08, r=0.05, angry=0.0, col='#f5e663')
group('e_moon', {'body': (b, None), **legs(), **arms(0.2, LH + 0.22, ln=0.12)}, EN)
# 기본 과제 — 테이프 붙은 골판지 상자
b = [box((0.6, 0.5, 0.48), (0, 0, LH + 0.24), '#c99a63', bevel=0.02), box((0.12, 0.505, 0.485), (0, 0, LH + 0.24), '#e1c48f', bevel=0.0),
     box((0.3, 0.01, 0.12), (0.12, -0.255, LH + 0.16), '#fbfbf7', bevel=0.0)] + eyes(LH + 0.34, -0.25, sep=0.14, r=0.06, angry=0.3)
group('e_box', {'body': (b, None), **legs(x=0.16), **arms(0.3, LH + 0.25)}, EN)
# 보조 사업 — 금화 + 초록 십자
b = [cyl(0.3, 0.1, (0, 0, LH + 0.33), '#f1c232', rot=(math.pi / 2, 0, 0), v=24, metal=0.8, rough=0.3), cyl(0.24, 0.11, (0, 0, LH + 0.33), '#e0ad1f', rot=(math.pi / 2, 0, 0), v=24, metal=0.8, rough=0.35),
     box((0.06, 0.02, 0.2), (0, -0.06, LH + 0.24), '#27ae60', bevel=0.0), box((0.2, 0.02, 0.06), (0, -0.06, LH + 0.24), '#27ae60', bevel=0.0)] + eyes(LH + 0.4, -0.06, sep=0.1, r=0.05)
group('e_coin', {'body': (b, None), **legs(x=0.1, h=0.17), **arms(0.29, LH + 0.33, ln=0.12)}, EN)
# 감사 지적 — 돋보기
b = [torus(0.2, 0.04, (0, 0, LH + 0.5), '#2c3e50', rot=(math.pi / 2, 0, 0)), cyl(0.18, 0.02, (0, 0, LH + 0.5), '#bfe6ff', rot=(math.pi / 2, 0, 0), v=24, rough=0.1),
     cyl(0.04, 0.32, (0, 0, LH + 0.15), '#7b4b2a', v=10)] + eyes(LH + 0.52, -0.03, sep=0.07, r=0.05, angry=0.35)
group('e_magnifier', {'body': (b, None), **legs(x=0.06, h=0.12), **arms(0.06, LH + 0.24, ln=0.14)}, EN)
# 예산 삭감 — 가위
b = [box((0.06, 0.04, 0.48), (-0.06, 0, LH + 0.42), '#bdc3c7', bevel=0.01, rot=(0, 0.35, 0), metal=0.8, rough=0.25), box((0.06, 0.04, 0.48), (0.06, 0.01, LH + 0.42), '#bdc3c7', bevel=0.01, rot=(0, -0.35, 0), metal=0.8, rough=0.25),
     torus(0.08, 0.025, (-0.12, 0, LH + 0.12), '#e74c3c', rot=(math.pi / 2, 0, 0)), torus(0.08, 0.025, (0.12, 0, LH + 0.12), '#e74c3c', rot=(math.pi / 2, 0, 0)), cyl(0.03, 0.06, (0, 0, LH + 0.3), '#7f8c8d', rot=(math.pi / 2, 0, 0))] + eyes(LH + 0.42, -0.04, sep=0.06, r=0.045, angry=0.45)
group('e_scissors', {'body': (b, None), **legs(x=0.1, h=0.12)}, EN)
# 용역 과제 — 나무 상자(크게)
b = [box((0.66, 0.56, 0.56), (0, 0, LH + 0.28), '#a87947', bevel=0.02)]
for z in (0.06, 0.5): b.append(box((0.68, 0.58, 0.06), (0, 0, LH + z), '#7d5530', bevel=0.0))
b.append(box((0.05, 0.585, 0.6), (-0.18, 0, LH + 0.28), '#7d5530', bevel=0.0, rot=(0, 0.75, 0)))
b += eyes(LH + 0.36, -0.29, sep=0.15, r=0.065, angry=0.3)
group('e_crate', {'body': (b, None), **legs(x=0.18, h=0.2), **arms(0.33, LH + 0.3)}, EN)
# 긴급 회의 — 종 달린 빨간 자명종
b = [cyl(0.26, 0.16, (0, 0, LH + 0.3), '#e74c3c', rot=(math.pi / 2, 0, 0), v=24), cyl(0.21, 0.02, (0, -0.08, LH + 0.3), '#fdfdfd', rot=(math.pi / 2, 0, 0), v=24),
     sph(0.1, (-0.17, 0, LH + 0.55), '#d4af37', scale=(1, 1, 0.7), metal=0.8, rough=0.3), sph(0.1, (0.17, 0, LH + 0.55), '#d4af37', scale=(1, 1, 0.7), metal=0.8, rough=0.3),
     box((0.02, 0.01, 0.13), (0, -0.095, LH + 0.36), '#222222', bevel=0), box((0.1, 0.01, 0.02), (0.04, -0.095, LH + 0.3), '#222222', bevel=0)] + eyes(LH + 0.32, -0.1, sep=0.09, r=0.04, angry=0.4)
group('e_bell', {'body': (b, None), **legs(x=0.12, h=0.16), **arms(0.26, LH + 0.3, ln=0.12)}, EN)
# R&D 과제 — 초록 약품 플라스크(보호막은 화면에서)
b = [sph(0.28, (0, 0, LH + 0.3), '#36d39a', emit=0.35, rough=0.25), sph(0.1, (-0.1, -0.2, LH + 0.42), '#c8ffe8', rough=0.1), sph(0.05, (0.12, -0.24, LH + 0.22), '#9effc9', rough=0.1), cyl(0.09, 0.22, (0, 0, LH + 0.63), '#d9f2ff', rough=0.1, v=14),
     cyl(0.11, 0.06, (0, 0, LH + 0.76), '#8e5a2b', v=14)] + eyes(LH + 0.36, -0.27, sep=0.1, r=0.055, angry=0.3)
group('e_flask', {'body': (b, None), **legs(x=0.13, h=0.18), **arms(0.28, LH + 0.3)}, EN)
# 의회 대응(보스) — 의사봉 든 나무 연단
b = [box((0.7, 0.5, 0.62), (0, 0, LH + 0.31), '#7a4a26', bevel=0.03), box((0.8, 0.6, 0.06), (0, 0, LH + 0.64), '#5b3519', bevel=0.02),
     box((0.5, 0.02, 0.3), (0, -0.26, LH + 0.36), '#2d5aa0', bevel=0.0), cyl(0.07, 0.02, (0, -0.275, LH + 0.36), '#f1c232', rot=(math.pi / 2, 0, 0), v=16, metal=0.7),
     cyl(0.02, 0.22, (0.2, -0.1, LH + 0.78), '#2b2b2b'), sph(0.045, (0.2, -0.1, LH + 0.9), '#2b2b2b')] + eyes(LH + 0.5, -0.255, sep=0.16, r=0.07, angry=0.5)
gav = [cyl(0.02, 0.3, (0.55, 0, LH + 0.45), '#5b3519', rot=(0, math.pi / 2, 0)), cyl(0.07, 0.18, (0.7, 0, LH + 0.45), '#3d2412')]
group('e_council', {'body': (b, None), **legs(x=0.2, h=0.2), 'armR': (gav, (0.38, 0, LH + 0.45)), 'armL': ([cyl(0.03, 0.2, (-0.48, 0, LH + 0.45), '#5b3519', rot=(0, math.pi / 2, 0)), sph(0.05, (-0.58, 0, LH + 0.45), '#f2d0b4')], (-0.38, 0, LH + 0.45))}, EN)
# 국정감사(최종 보스) — 붉은 눈의 바인더 탑 + 마이크
b = []
cols = ['#2c3e50', '#8e2b2b', '#1f4e79', '#2c3e50', '#6c2b8e']
for k, c in enumerate(cols):
    b.append(box((0.62 - k * 0.03, 0.42, 0.2), (0.02 * (k % 2), 0, LH + 0.1 + k * 0.2), c, bevel=0.02))
    b.append(box((0.5 - k * 0.03, 0.43, 0.15), (0.02 * (k % 2) + 0.04, 0, LH + 0.1 + k * 0.2), '#f3f1ea', bevel=0.0))
b += [box((0.36, 0.02, 0.14), (0, -0.225, LH + 0.7), '#c0392b', bevel=0.0, emit=0.8)]
b += eyes(LH + 0.92, -0.22, sep=0.13, r=0.07, angry=0.6, col='#ffdddd', pupil='#e01b24')
mic = [cyl(0.02, 0.36, (0.5, -0.05, LH + 0.75), '#333333', rot=(0, math.pi / 2, 0)), sph(0.07, (0.68, -0.05, LH + 0.75), '#555555', scale=(1.3, 1, 1))]
group('e_gukgam', {'body': (b, None), **legs(x=0.2, h=0.2), 'armR': (mic, (0.32, 0, LH + 0.75)), 'armL': ([cyl(0.03, 0.22, (-0.43, 0, LH + 0.7), '#2c3e50', rot=(0, math.pi / 2, 0)), sph(0.06, (-0.55, 0, LH + 0.7), '#f2d0b4')], (-0.32, 0, LH + 0.7))}, EN)

def export(coll, path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in coll.all_objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True, export_yup=True)

export(EN, os.path.join(OUT, 'enemies.glb'))

# ════════════════════════════════════════════════════════════
# 2) 소품(인력용·발사체·지킬 곳·입구)
# ════════════════════════════════════════════════════════════
reset(); MATS.clear()
PR = bpy.data.collections.new('props'); bpy.context.scene.collection.children.link(PR)
def solo(name, objs): return group(name, {'body': (objs, None)}, PR)
# 이동식 파티션 — 1칸 폭, 파란 천 + 알루미늄 틀
solo('p_partition', [box((0.96, 0.08, 1.05), (0, 0, 0.6), '#4f78a8', bevel=0.01, rough=0.95), box((1.0, 0.1, 0.05), (0, 0, 1.15), '#c7ccd3', bevel=0.01, metal=0.6, rough=0.35),
                     box((0.05, 0.1, 1.1), (-0.5, 0, 0.58), '#c7ccd3', bevel=0.01, metal=0.6), box((0.05, 0.1, 1.1), (0.5, 0, 0.58), '#c7ccd3', bevel=0.01, metal=0.6),
                     box((0.3, 0.4, 0.04), (-0.4, 0, 0.02), '#9aa2ad', bevel=0.01), box((0.3, 0.4, 0.04), (0.4, 0, 0.02), '#9aa2ad', bevel=0.01),
                     box((0.18, 0.01, 0.14), (0.15, -0.046, 0.8), '#fff176', bevel=0), box((0.14, 0.01, 0.12), (-0.2, -0.046, 0.62), '#ff9ecb', bevel=0)])
# 문서 파쇄기 — 낮은 함(바닥 덫)
solo('p_shredder', [box((0.56, 0.4, 0.3), (0, 0, 0.15), '#3b3f48', bevel=0.03), box((0.6, 0.44, 0.08), (0, 0, 0.33), '#2b2e35', bevel=0.02), box((0.4, 0.04, 0.02), (0, 0, 0.375), '#111111', bevel=0),
                    cyl(0.03, 0.01, (0.22, -0.15, 0.375), '#2ecc71', emit=3.0), box((0.3, 0.005, 0.16), (0, -0.205, 0.17), '#cfd3da', bevel=0)])
# 복합기
solo('p_copier', [box((0.8, 0.62, 0.62), (0, 0, 0.31), '#e8eaee', bevel=0.03), box((0.8, 0.62, 0.12), (0, 0, 0.68), '#d5d8de', bevel=0.02), box((0.5, 0.4, 0.04), (0, 0, 0.75), '#3a3f4a', bevel=0.01),
                  box((0.24, 0.02, 0.12), (0.2, -0.32, 0.6), '#3a8ee8', bevel=0.0, emit=1.5), box((0.5, 0.3, 0.03), (0, -0.4, 0.42), '#fbfbf7', bevel=0.0),
                  box((0.7, 0.02, 0.1), (0, -0.315, 0.2), '#b8bcc4', bevel=0), box((0.7, 0.02, 0.1), (0, -0.315, 0.06), '#b8bcc4', bevel=0)])
# 정수기
solo('p_water', [box((0.36, 0.36, 0.9), (0, 0, 0.45), '#f2f4f7', bevel=0.03), cyl(0.15, 0.4, (0, 0, 1.12), '#7fc8ff', rough=0.05, v=16), box((0.06, 0.06, 0.06), (-0.07, -0.2, 0.6), '#3498db', bevel=0.01), box((0.06, 0.06, 0.06), (0.07, -0.2, 0.6), '#e74c3c', bevel=0.01)])
# 서류 카트(인력) — 바퀴 달린 수레 + 서류 더미
cart = [box((0.7, 0.46, 0.06), (0, 0, 0.22), '#7f8c8d', bevel=0.01, metal=0.5), box((0.7, 0.46, 0.06), (0, 0, 0.6), '#7f8c8d', bevel=0.01, metal=0.5)]
for sx in (-1, 1):
    for sy in (-1, 1):
        cart.append(cyl(0.02, 0.5, (sx * 0.33, sy * 0.21, 0.4), '#95a5a6', metal=0.6, v=8)); cart.append(sph(0.06, (sx * 0.3, sy * 0.19, 0.06), '#222222'))
cart += [box((0.32, 0.4, 0.2), (-0.14, 0, 0.73), '#fbfbf7', bevel=0.005), box((0.3, 0.38, 0.14), (0.18, 0, 0.7), '#f4e3b3', bevel=0.005), box((0.32, 0.4, 0.12), (0.0, 0, 0.32), '#e8c27a', bevel=0.005)]
solo('p_cart', cart)
# 굴러가는 카트(발사체) — 위와 같은 꼴, 서류 더 높이
solo('x_cart', [o for o in [box((0.7, 0.46, 0.06), (0, 0, 0.22), '#c0392b', bevel=0.01), box((0.32, 0.4, 0.3), (-0.12, 0, 0.4), '#fbfbf7', bevel=0.005), box((0.3, 0.38, 0.24), (0.18, 0, 0.37), '#f4e3b3', bevel=0.005)]] + [sph(0.06, (sx * 0.3, sy * 0.19, 0.06), '#222222') for sx in (-1, 1) for sy in (-1, 1)])
# 로봇(메신저봇·AI) — 모니터 머리 + 바퀴 몸
bot = [box((0.42, 0.3, 0.32), (0, 0, 0.62), '#2d3440', bevel=0.04), box((0.36, 0.02, 0.24), (0, -0.155, 0.62), '#3be0c6', bevel=0.01, emit=1.8),
       box((0.08, 0.01, 0.06), (-0.08, -0.168, 0.65), '#0d2b33', bevel=0), box((0.08, 0.01, 0.06), (0.08, -0.168, 0.65), '#0d2b33', bevel=0),
       cyl(0.06, 0.22, (0, 0, 0.36), '#9aa2ad', metal=0.6, v=12), cyl(0.2, 0.12, (0, 0, 0.13), '#e8eaee', v=20, bevel=0.0), cyl(0.012, 0.18, (0.12, 0, 0.86), '#9aa2ad', v=6), sph(0.035, (0.12, 0, 0.96), '#ff5e57', emit=3.0)]
solo('p_bot', bot)
# 결재함(지킬 곳) — 3단 서류 트레이 + 도장
inbox = []
for k in range(3):
    inbox += [box((0.62, 0.46, 0.03), (0, 0, 0.42 + k * 0.2), '#34495e', bevel=0.005, metal=0.4), box((0.62, 0.03, 0.12), (0, -0.22, 0.47 + k * 0.2), '#34495e', bevel=0.005, metal=0.4),
              box((0.5, 0.36, 0.06 + 0.03 * k), (0, 0.02, 0.47 + k * 0.2), '#fbfbf7', bevel=0.003)]
inbox += [cyl(0.03, 0.42, (sx * 0.29, sy * 0.2, 0.42), '#2c3e50', v=8) for sx in (-1, 1) for sy in (-1, 1)]
inbox += [box((0.9, 0.7, 0.4), (0, 0, 0.2), '#7f5539', bevel=0.02), cyl(0.06, 0.12, (0.36, 0.25, 0.46), '#c0392b', v=14), cyl(0.04, 0.1, (0.36, 0.25, 0.57), '#5b3519', v=10)]
solo('p_inbox', inbox)
# 입구 — 엘리베이터 문틀(벽 두께 안에 서는 문)
solo('p_elevator', [box((1.0, 0.2, 1.6), (0, 0, 0.8), '#7b8794', bevel=0.02, metal=0.5, rough=0.35), box((0.42, 0.04, 1.4), (-0.22, -0.11, 0.7), '#c9d1da', bevel=0.005, metal=0.8, rough=0.25),
                    box((0.42, 0.04, 1.4), (0.22, -0.11, 0.7), '#c9d1da', bevel=0.005, metal=0.8, rough=0.25), box((0.3, 0.05, 0.14), (0, -0.11, 1.5), '#111111', bevel=0.0),
                    box((0.06, 0.02, 0.06), (0, -0.14, 1.5), '#ff6b3d', bevel=0, emit=3.0)])
# 발사체
solo('x_paper', [sph(0.09, (0, 0, 0), '#fbfbf7', seg=7)])
solo('x_stamp', [cyl(0.07, 0.07, (0, 0, 0), '#c0392b', v=12), cyl(0.03, 0.12, (0, 0, 0.09), '#5b3519', v=8), sph(0.045, (0, 0, 0.16), '#5b3519')])
solo('x_mail', [box((0.22, 0.03, 0.15), (0, 0, 0), '#f5f7fb', bevel=0.005), box((0.15, 0.032, 0.15), (0, -0.003, 0.03), '#dde3ee', bevel=0, rot=(0, math.pi / 4, 0))])
solo('x_bundle', [box((0.28, 0.2, 0.12), (0, 0, 0), '#fbfbf7', bevel=0.01), box((0.3, 0.06, 0.13), (0, 0, 0), '#c0392b', bevel=0.0)])
solo('x_query', [box((0.2, 0.02, 0.26), (0, 0, 0), '#ffe8e0', bevel=0.003), box((0.14, 0.022, 0.02), (0, 0, 0.06), '#c0392b', bevel=0)])
export(PR, os.path.join(OUT, 'props.glb'))

# ════════════════════════════════════════════════════════════
# 3) 사무실 가구 — Kenney Furniture Kit(CC0)를 한 파일로
# ════════════════════════════════════════════════════════════
reset(); MATS.clear()
OF = bpy.data.collections.new('office'); bpy.context.scene.collection.children.link(OF)
KEEP = ['desk', 'deskCorner', 'chairDesk', 'computerScreen', 'computerKeyboard', 'laptop', 'bookcaseClosedWide', 'bookcaseOpen', 'books', 'kitchenCabinet', 'kitchenCoffeeMachine',
        'kitchenFridge', 'kitchenMicrowave', 'loungeSofa', 'loungeChair', 'pottedPlant', 'plantSmall1', 'plantSmall2', 'table', 'chair', 'trashcan', 'lampSquareFloor', 'cardboardBoxClosed',
        'rugRectangle', 'speaker', 'televisionModern', 'coatRackStanding', 'sideTable', 'radio', 'paneling']
for k in KEEP:
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(FURN_DIR, k + '.glb'))
    new = [o.name for o in bpy.data.objects if o.name not in before]
    meshes = [bpy.data.objects[n] for n in new if bpy.data.objects[n].type == 'MESH']
    others = [n for n in new if bpy.data.objects[n].type != 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes: o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    o = join(meshes, 'f_' + k)
    for n in others:
        x = bpy.data.objects.get(n)
        if x: bpy.data.objects.remove(x)
    for c in o.users_collection: c.objects.unlink(o)
    OF.objects.link(o)
    print('가구', k, [round(v, 2) for v in o.dimensions])
export(OF, os.path.join(OUT, 'office.glb'))
print('끝')
