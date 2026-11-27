# 따닥 위키

따닥(DDD 14기 WEB 1팀)의 기획·정책 라이브 위키입니다. 개발과 디자인은 이 위키를 기준으로 진행합니다.

- 사이트: https://ddd-community.github.io/DDD_14_TTADAK/
- 기능마다 **정책서**(`docs/policy/`, 원본)와 **화면 설계서**(`docs/screens/`)를 둡니다. 화면 설계서는 정책 번호로 정책서와 이어집니다.

## 쓰는 법

- 페이지는 `wiki/docs/` 아래 Markdown 파일입니다.
- 정책은 `<div class="policy">` 안에 `- **UPL-01** 규칙 한 문장` 형식으로 쓰고, "확정 / 검토 중 / 미결정" 세 묶음으로 나눕니다.
- 한 번 붙인 정책 번호는 바꾸지 않습니다. 없어진 정책은 "폐기"로 표시합니다.
- 화면 설계서는 화면마다 `SCR-UPL-01` 같은 ID, 와이어프레임, "번호 | 요소 | 액션 | 상태 | 정책" 표를 둡니다.
- 글꼴은 Pretendard(CDN), 색은 무채색입니다. 서비스 메인 컬러는 `docs/.vitepress/theme/style.css`의 `--accent`, `--accent-text`, `--accent-soft` 세 값만 바꿔 넣습니다.
- 내용을 바꾸면 `docs/guide/changelog.md`에 한 줄을 남깁니다.

## 로컬에서 보기

```bash
cd wiki
npm install
npm run dev
```

`wiki/`가 바뀐 채로 `main`에 머지되면 GitHub Actions(`.github/workflows/wiki.yml`)가 GitHub Pages로 배포합니다. PR에서는 빌드만 확인합니다.

## 댓글

페이지 아래 댓글(Giscus)은 이관 전 저장소 [soohy00/ttadak-wiki](https://github.com/soohy00/ttadak-wiki/discussions)의 Discussions에 저장합니다. 이 저장소로 옮기려면 DDD-Community 조직에 Giscus 앱을 설치하고 Discussions를 켜야 해서, 그 전까지는 기존 저장소를 씁니다. 옮길 때는 `docs/.vitepress/theme/Comments.vue`의 `data-repo`, `data-repo-id`, `data-category-id`만 바꾸면 됩니다.

## 라이선스

- 글꼴: Pretendard, SIL Open Font License 1.1 (jsDelivr CDN으로 불러옴)
