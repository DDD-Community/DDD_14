# Client

타닥 웹 프론트엔드. React 19 · TypeScript 7 · Vite · Tailwind v4 · TanStack Query · zustand.
에이전트 세션은 **레포 루트에서 시작**하고(서버 코드도 참고할 수 있다), 명령은 `client/`에서 pnpm으로 실행한다.

## 명령어

| 명령                            | 용도                                                                  |
| ------------------------------- | --------------------------------------------------------------------- |
| `pnpm verify`                   | **작업 완료 전 필수.** typecheck → lint → format:check → test → build |
| `pnpm verify:fast`              | 작업 중 빠른 확인 (typecheck + lint)                                  |
| `pnpm test [파일]`              | 테스트 실행 (전체 또는 특정 파일)                                     |
| `pnpm lint:fix` / `pnpm format` | 자동 수정                                                             |
| `pnpm docs:check`               | 문서 링크·ADR 번호·환경 변수 표 정합성 검사                           |
| `pnpm dev`                      | 개발 서버 (http://localhost:5173)                                     |

## 완료의 정의

1. `pnpm verify`가 통과한다. 실행한 명령과 결과를 보고에 포함한다.
2. 화면을 바꿨다면 브라우저에서 직접 확인한다 → [ui-verification](docs/rules/ui-verification.md)
3. 관련 `specs/`·`adr/`를 코드와 맞춘다 → [documentation](docs/rules/documentation.md)
4. 테스트를 지우거나 skip해서 통과시키지 않는다. 테스트가 틀렸다고 판단되면 멈추고 사람에게 묻는다.

## 작업 방식

- 구현 전에 `docs/plans/`에 plan을 쓰고(`- 상태: 진행 중`), 진행하면서 체크리스트와 진행 로그를 갱신한다.
- 한 번에 하나의 기능 슬라이스만 구현한다.
- 새 의존성 추가는 ADR 대상이다. 설치 전에 사람에게 먼저 묻는다.
- lint 오류 메시지에는 고치는 방법이 적혀 있다. 규칙을 끄지 말고 메시지대로 고친다.
- 반복 절차는 스킬을 쓴다: `client-new-feature`(기능 구현), `client-verify-ui`(화면 확인), `client-write-adr`(결정 기록), `client-review-changes`(변경 리뷰).
- 훅이 스킬 실행을 요청하면 그대로 따른다. 스킬을 자동으로 찾지 못하면(예: 루트에서 시작한 Codex) `client/.agents/skills/<스킬 이름>/SKILL.md`를 읽고 따른다.
- 프론트엔드 작업에서는 `server/`를 참고만 하고, 사용자가 시키지 않으면 고치지 않는다. `server/`의 규칙·스킬·작업 절차는 백엔드 세션(`server/`에서 시작)용이다.

## 하네스 위치

| 무엇           | 위치                                                                 |
| -------------- | -------------------------------------------------------------------- |
| 스킬           | `.agents/skills/` (원본), `.claude/skills/` (Claude용 링크)          |
| 외부 스킬 잠금 | `skills-lock.json` (`npx skills add`는 `client/`에서 실행)           |
| 훅 스크립트    | `scripts/agent-hooks/`                                               |
| 훅 등록        | 레포 루트 `.claude/settings.json`, `.codex/hooks.json` (루트 세션용) |
| git hook       | 레포 루트 `lefthook.yml`. `pnpm install` 때 `prepare`가 등록한다     |

## 문서 지도

구현 전에 이 순서로 좁혀 읽는다. `docs/` 아래 문서를 쓰거나 옮길 때는 반드시 [documentation](docs/rules/documentation.md)을 먼저 읽는다.

1. `docs/rules/`: 반드시 지킬 제약
   - [documentation](docs/rules/documentation.md): 문서 분류·작성 규칙, plan 형식
   - [testing](docs/rules/testing.md): 무엇을 어떻게 테스트하나
   - [code-review](docs/rules/code-review.md): 리뷰 체크리스트
   - [ui-verification](docs/rules/ui-verification.md): 화면 확인 절차
   - [git-workflow](docs/rules/git-workflow.md): 브랜치·커밋·PR
2. `docs/specs/`: 현재 코드와 일치하는 source of truth
   - [client-architecture](docs/specs/client-architecture.md): 폴더 구조, 의존 방향
   - [client-tooling](docs/specs/client-tooling.md): 도구, 라이브러리 사용 규칙, 환경 변수, 스크립트
3. `docs/adr/`: 결정의 배경
4. `docs/plans/`: 진행 중인 계획 (확정된 규칙이 아님)

## 하네스 개선

같은 실수가 반복되면 고칠 위치를 이 순서로 고른다.
lint·타입·테스트 → 스크립트·스킬 → `docs/rules/` → 이 파일(모든 작업에 해당할 때만).
이 파일은 100줄을 넘기지 않는다.
