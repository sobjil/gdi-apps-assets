# 과제 지옥 3D 모델 출처

모두 CC0(Creative Commons Zero — 출처 표시 없이 써도 된다). 과제 지옥 2(3D 사무실 미로 디펜스, 2026-10-09)에 쓴다.

- `m/c_male?.glb`·`m/c_female?.glb` (12명) — Kenney (www.kenney.nl) **Mini Characters**. 쓰는 동작 13가지만 남겼다(`game/shared/tools/slim-models.mjs`): idle·walk·sit·die·pick-up·emote-yes·emote-no·holding-right·holding-right-shoot·holding-both-shoot·attack-melee-right·attack-kick-right·interact-right
- `m/office.glb` — Kenney **Furniture Kit** 가구 30가지를 한 파일로(이름 = `f_<원래 이름>`). 압축(양자화)해서 노드에 배율이 붙어 있다 — 꺼내 쓸 땐 한 겹 감싸고 바깥만 키운다
- `m/enemies.glb` — 업무(적) 22종 「서류 괴물」. 이 게임에서 블렌더로 코드로 만들었다(`src/build.py`, CC0). 뿌리 이름 = `e_<모델>`, 부위 = `body`·`legL`·`legR`·`armL`·`armR`·`wingL`·`wingR`(화면이 직접 흔든다)
- `m/props.glb` — 이동식 파티션·문서 파쇄기·복합기·정수기·서류 카트·로봇·결재함·엘리베이터·발사체(종이 뭉치·도장·메일·서류 다발·질의서·굴러가는 카트). 같은 스크립트

다시 굽기: `blender -b -P src/build.py -- <Kenney Furniture Kit 의 GLTF format 폴더> <출력 폴더>` 뒤 gltf-transform 으로 dedup·weld·quantize.
