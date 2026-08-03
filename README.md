# gdi-apps-assets

딸깍 개발실 대용량 공개 자산(다운로드 배포용 — 메인 레포 배포 경량화).

현재 보관 중인 것 = **Real-ESRGAN 로컬 업스케일 서버 zip**(릴리스 `esrgan-v1`).
자료실(`https://sobjil.com/downloads/`)이 이 릴리스를 직접 링크한다.
갱신은 `gh release upload esrgan-v1 <zip> --repo sobjil/gdi-apps-assets --clobber`.

## 딸깍 위키 만화는 여기 없다 (2026-08-03 이전)

위키 학습만화 이미지는 **`sobjil/gdi-wiki-assets`** 로 옮겼다.
여기 있던 1세대 만화 1,985컷은 결함 수정본(472편·5,820컷)으로 교체되면서
**히스토리째 삭제**했다 — 참조가 끊긴 이미지를 공개 저장소에 남기지 않기 위해서다.
서버 기본값(`server/wiki.js` `WIKI_ASSETS_REPO`)도 새 저장소를 가리킨다.
