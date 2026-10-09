# 새벽바라기 3D 모델 출처

모두 CC0(Creative Commons Zero — 출처 표시 없이 써도 된다). 3D 리뉴얼(2026-10-05)에 쓰려고 골라 GLB 로 바꿨다.

- `m/ch/zombie.glb` — Quaternius (quaternius.com) **Animated Zombie**. FBX 를 FBX2glTF 로 바꾸고 색 그림(ZombieTexture.png)을 넣었다. 동작: Walk·Run·Crawl·Bite·Idle
- `m/ch/*.glb`(casual·hoodie·suit·worker·swat·farmer·punk·beach·adventurer) — Quaternius **Ultimate Modular Characters**(CharacterArmature, 동작 24가지). FBX → GLB, 쓰지 않는 마디를 줄였다(`game/shared/tools/slim-models.mjs`)
- `m/ck/` — Kenney (www.kenney.nl) **City Kit (Commercial)** 건물
- `m/rd/` — Kenney **City Kit (Roads)** 전봇대·가로등·쓰레기통·공사 표지
- `m/car/` — Kenney **Car Kit** 승용차·승합차·택시·트럭 등

각 폴더의 `Textures/colormap.png` 는 그 묶음 것이다(묶음마다 다르다 — 섞지 말 것).
- `m/an/wolf.glb`·`husky.glb` — Quaternius **Ultimate Animated Animals**(CC0). glTF 를 GLB 로 묶고 동작 이름을 게임 것으로 바꿨다(Walk·Gallop→Run·Attack→Bite·Idle·Death·Idle_HitReact1→Scream). 감염견(Z-07)·무리장(M-07)
- `m/an/crow.glb` — 이 게임에서 블렌더로 코드로 만들었다(`src/crow.py`, CC0). 날갯짓(Walk·Run)·활공(Idle)·내리꽂기(Bite)·떨어짐(Death). 까마귀 떼(Z-08)
- `m/props.glb` — 손에 드는 무기 18가지 + 도는 프라이팬(W-03)·드론(W-24), 이 게임에서 블렌더로 코드로 만들었다(`src/props.py`, CC0). 물체 이름 = 무기 id(W-01 …), 쥐는 자리 = 원점
- `m/map.glb` — 밤 2-7 지도 모델 27가지(아파트·화단·놀이터·지하철 기둥·개찰구·선로·전동차·학교·스탠드·골대·병상·병원 문·버스·송신탑·실외기·옥상 난간·불탄 차 등), 이 게임에서 블렌더로 코드로 만들었다(`src/map.py`, CC0). 이름이 `-seg` 로 끝나는 것은 이어 붙이는 한 칸
- 사람 모델(생존자·좀비·보스)은 믹사모라 여기 두지 않는다 — sobjil.com 서버 `/game-assets/dawn/mx1/`(믹사모 약관상 원본 단독 배포 금지)

블렌더로 다시 만들기: `blender -b --python src/crow.py -- m/an/crow.glb` · `blender -b --python src/props.py -- m/props.glb` · `blender -b --python src/map.py -- m/map.glb`(블렌더 5.2)
