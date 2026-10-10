# 경북귀농일기 자산 출처

모두 CC0(퍼블릭 도메인) — 출처 표기 의무는 없지만 적어 둔다.

| 파일 | 원본 | 작가 | 라이선스 |
|---|---|---|---|
| `m/nature.glb` | Stylized Nature MegaKit — 덤불 2·꽃 1·풀 3·클로버·풀포기·바위 3·자갈 3·버섯·디딤돌 3 (18종, 그림 512px webp 로 줄임) | Quaternius (https://quaternius.itch.io/stylized-nature-megakit) | CC0 1.0 |

만든 법(2026-10-10): `gltf-transform merge <18개 .gltf> → optimize --texture-compress webp --texture-size 512 --compress false --join false --instance false --flatten false`. 잎·풀 그림은 원래 단색 덩어리(엔진에서 색을 입힘)라 게임이 불러올 때 모양(알파)만 남기고 색을 입힌다(`game/farmstory/p0/js/nature.js`).
