# 0004. 에이전트 하네스 구성 (훅·스킬·검증)

## 상태 (Status)

제안됨 (Proposed) — 2026-11-22. **일부 대체됨 (Superseded in part) — 2026-11-26, [ADR 0005](0005-harness-per-area.md)**

> 스킬·훅 스크립트의 위치와 팀 스킬 이름은 ADR 0005가 대체한다. 검증·스킬 자동 요청 방식 등 나머지는 유지한다.

## 배경 (Context)

FE 개발자 2명이 Claude Code를 주력으로, Claude 사용 한도를 다 쓰면 Codex로 이어서 개발한다. 에이전트가 규칙을 문서로만 안내받으면 놓치는 경우가 생기고, "완료"를 증거 없이 선언하기도 한다. 그래서 작업 전 안내(가이드)와 작업 후 검사(센서)를 갖추고, 두 도구에서 같은 규칙·스킬·훅이 동작하게 해야 했다. 조사와 전체 설계는 이 결정을 도입한 PR의 계획 문서(`docs/plans/2026-11-22-harness-engineering-*.md`, 개요 1개 + 주제별 4개. 리뷰 후 삭제되어 git 이력에 남는다)에 있다.

## 결정 (Decision)

| 영역        | 결정                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------ |
| 규칙 원본   | `AGENTS.md`. Claude는 `CLAUDE.md`의 `@AGENTS.md`로 읽는다                                                    |
| lint        | 타입 인식 규칙(`oxlint-tsgolint`) + 커스텀 플러그인(`lint-plugins/ttadak.js`). 메시지에 고치는 방법을 쓴다   |
| git hook    | lefthook: pre-commit(Prettier, oxlint), commit-msg(Conventional Commits)                                     |
| CI          | GitHub Actions: `pnpm verify` + `pnpm docs:check`                                                            |
| 에이전트 훅 | `tools/agent-hooks/`: `stop-gate`(검증 + 스킬 자동 요청), `plan-gate`, `session-start`, `format-edited-file` |
| 스킬        | 원본은 `.agents/skills/`, Claude용 `.claude/skills/`는 심볼릭 링크                                           |
| 팀 스킬     | `new-feature`, `review-changes`, `verify-ui`, `write-adr`                                                    |
| 외부 스킬   | `playwright-cli`(Microsoft), `vercel-react-best-practices`, `web-design-guidelines`(Vercel Labs)             |
| 브라우저    | `@playwright/cli`를 devDependency로 둔다                                                                     |

스킬이 확률적으로 선택되는 문제는 훅이 상황(plan 없음, 화면 변경, 새 의존성, 코드 변경)을 감지해 해당 스킬을 요청하는 방식으로 해결한다.

고려한 대안:

- **husky**: `package.json`이 `client/`에 있어서 git 루트와 맞추는 설정이 필요하다. lefthook은 루트 설정 파일 하나로 끝난다.
- **commitlint**: 의존성이 많다. 형식 검사는 짧은 스크립트로 충분하다.
- **Claude 전용 구성**: Codex로 넘어가면 규칙·스킬이 끊긴다.
- **프롬프트 키워드로 스킬 연결(UserPromptSubmit 훅)**: 분류가 불안정하고 매번 컨텍스트를 쓴다.
- **Claude GitHub App으로 PR 리뷰**: 조직 레포에 앱 설치가 필요하다. 작업 종료 시 훅으로 리뷰를 요청하면 설치 없이 두 도구에서 동작한다.

## 결과 (Consequences)

- 검증과 리뷰가 사람이 시키지 않아도 매번 돈다. 최종 방어선은 도구와 무관한 lefthook과 CI가 맡는다.
- 자동 스킬 요청은 사용량을 쓴다. 같은 변경에는 한 번만 요청하고, `TTADAK_AUTO_SKILLS=0`으로 끌 수 있다.
- `stop-gate`는 같은 작업에서 검증이 3번 넘게 실패하면 더 막지 않는다(무한 반복 방지). 전체를 끄려면 `TTADAK_STOP_GATE=0`.
- `plan-gate`는 작은 수정에도 plan을 요구한다. 짧은 plan으로 충분하고, `TTADAK_PLAN_GATE=0`으로 끌 수 있다.
- Codex 훅 형식은 공식 문서를 직접 확인하지 못했다. 도입 후 Codex `/hooks`로 확인한다.
- 심볼릭 링크는 Windows에서 문제가 될 수 있다.
