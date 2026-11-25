# Git Workflow Rule

브랜치, 커밋, PR 규칙이다.

## 브랜치

- `main`은 보호한다. 작업은 `main`에서 딴 짧은 브랜치에서 한다.
- 브랜치 이름: `feat/`, `fix/`, `chore/`, `docs/`, `refactor/`, `test/` + 짧은 설명. 예: `feat/login-form`

## 커밋

- Conventional Commits 형식: `<type>: <한국어 요약>`. 범위가 필요하면 `<type>(<scope>): <요약>`.
- type: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`, `ci`, `build`, `revert`
- commit-msg 훅이 형식을 검사한다. merge·revert 커밋은 검사하지 않는다.

## PR

- 기능 슬라이스 하나, 15분 안에 리뷰할 수 있는 크기로 만든다.
- PR 템플릿을 채운다. 검증 증거와 "하네스 피드백"을 빠뜨리지 않는다.
- 상대방 승인 1명을 받은 뒤 squash merge한다.
- `shared/`, AGENTS.md, lint 설정처럼 둘 다 영향을 받는 변경은 작은 PR로 먼저 머지한다.
- ADR 번호가 겹치면 나중에 머지하는 쪽이 번호를 바꾼다. CI의 `pnpm docs:check`가 중복을 막는다.

## 커밋 전 자동 검사 (lefthook)

`client/`에서 `pnpm install`을 하면 자동으로 등록된다. 설정은 루트 `lefthook.yml`.

| 시점         | 검사                                                     |
| ------------ | -------------------------------------------------------- |
| `pre-commit` | staged 파일에 Prettier 적용, oxlint 검사                 |
| `commit-msg` | 커밋 메시지 형식 (`client/scripts/check-commit-msg.mjs`) |
