# 딸깍 GranD prIx 자산 출처

- `m/f1.glb` — scaranto 「Racing car」 (poly.pizza/m/EMcTJiXibv), CC0. 내 차(기본 스킨). 파일은 고치지 않았다(팀 색은 게임이 차체 재질 색만 바꾼다)
- `m/race.glb` · `m/race-future.glb` · `m/Textures/colormap.png` — Kenney **Car Kit** 3.1 (www.kenney.nl), CC0. 경쟁 차. 파일은 고치지 않았다(팀 색은 게임이 팔레트 두 칸만 다시 칠한다)
- `m/sports.glb` — Quaternius 「Sports Car」 (poly.pizza/m/1mkmFkAz5v), CC0. 경쟁 차. 파일은 고치지 않았다(바퀴 축은 게임이 불러올 때 맞춘다)
- 스킨 모델(2026-10-09) — `m/truck.glb` · `m/suv.glb` · `m/truck-flat.glb`(픽업 스킨) — Kenney **Car Kit** 3.1, CC0, 고치지 않았다(그림은 `m/Textures/colormap.png` 를 같이 쓴다)
- `m/schoolbus.glb` — Quaternius **Public Transport** 「SchoolBus」(quaternius.com/packs/publictransport.html), CC0. FBX → GLB 로만 바꿨다
- `m/horse.glb` · `m/horse-white.glb` · `m/husky.glb` — Quaternius **Ultimate Animated Animals**(quaternius.com/packs/ultimateanimatedanimals.html), CC0. 동작은 `Gallop`·`Walk`·`Idle` 만 남기고 키프레임을 3분의 1로 솎았다(2MB → 0.3MB). 말·유니콘·마차·전차·강아지 산책 스킨
- `sfx/engine.ogg` — domasx2 「racing car engine sound loops」 loop_0 (opengameart.org/content/racing-car-engine-sound-loops), CC0. 44.1kHz 단일 채널 ogg 로 바꿨다
- `sfx/skid.ogg` — Tom Haigh(audible-edge), qubodup 정리 「Car tire squeal skid loop」 (opengameart.org/content/car-tire-squeal-skid-loop), **CC-BY 3.0** — 출처를 남긴다. 44.1kHz 단일 채널 ogg 로 바꿨다

쓰는 곳 = GDI-Apps `game/grandprix/render/carmodel.js` · `render/sound.js`.

## 풍경·하늘(2026-10-05, 리뉴얼 그래픽)

- `s/rk/` — Kenney **Racing Kit** 2.0 (www.kenney.nl), CC0. 관중석·출발 문·깃발·광고판·조명탑·천막·차고. 파일은 고치지 않았다(광고판 그림은 게임이 바꿔 끼운다)
- `s/nk/` — Kenney **Nature Kit** 2.1 (www.kenney.nl), CC0. 나무·덤불·바위·꽃·수련·카누·장작·울타리·옥수수·밀
- `s/ck/` · `s/ck/Textures/colormap.png` — Kenney **City Kit (Suburban)** 2.0 (www.kenney.nl), CC0. 집
- `s/mc/` — Kenney **Mini Characters** 1.0 (www.kenney.nl), CC0. 관중. `idle`·`sit` 동작만 남기고 줄였다(`game/shared/tools/slim-models.mjs`) — 게임이 그 자세로 굳혀 인스턴스로 그린다
- `s/an/cow.glb` — Quaternius 「Cow」 (poly.pizza/m/5XSc2Fka3F), CC0 · `s/an/sheep.glb` — Quaternius 「Sheep」 (poly.pizza/m/C39AUXUUes), CC0. `Idle` 동작만 남겼다
- `sky/sky-clear.jpg` — Poly Haven 「Kloofendal 48d Partly Cloudy (Pure Sky)」 · `sky/sky-rain.jpg` — 「Kloofendal Overcast (Pure Sky)」 · `sky/sky-snow.jpg` — 「Snow Field (Pure Sky)」 (polyhaven.com, Greg Zaal·Jarod Guest 외), CC0. 4k HDR 을 지평선 아래 6도부터 천정까지 잘라 선형 값 × k 를 sRGB JPG 로 담았다(`sky.json` 의 `k` — 게임이 1/k 를 곱해 되돌린다). 맑은 하늘은 해 방위를 게임 해 방위로 돌렸다
