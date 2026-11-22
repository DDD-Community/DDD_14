# FE 하네스: 협업과 도구

- 상태: 완료
- 상위 문서: [개요](2026-11-22-harness-engineering-plan.md)

## 1. 협업 워크플로

**작업 사이클**

| 단계 | 누가              | 할 일                                                  |
| ---- | ----------------- | ------------------------------------------------------ |
| 1    | 사람              | 작업 선택 → `plans/YYYY-MM-DD-<topic>-plan.md` 작성    |
| 2    | 에이전트          | 탐색 → 계획 → 테스트 → 구현 → `verify` → 브라우저 확인 |
| 3    | 에이전트          | 관련 spec·adr 갱신, PR 본문 초안                       |
| 4    | 에이전트 → 작성자 | 작업 종료 시 자동 AI 리뷰 반영 → 작성자가 PR 생성      |
| 5    | 상대방            | 리뷰·승인                                              |
| 6    | 작성자            | squash merge, plan 정리                                |

**규칙**

| 항목      | 제안                                                                       |
| --------- | -------------------------------------------------------------------------- |
| PR 크기   | 기능 슬라이스 하나, 15분 안에 리뷰할 수 있게                               |
| 브랜치    | `main` 보호(상대방 승인 1명 필수) + `feat/` `fix/` `chore/` `docs/`        |
| 커밋      | Conventional Commits (지금 쓰는 `chore:` `docs:` 명문화) + commit-msg hook |
| ADR 번호  | `main` 기준 다음 번호. 충돌하면 나중에 머지하는 쪽이 변경                  |
| plan 정리 | 상단에 `상태: 진행 중 \| 완료`. 완료 PR에서 삭제 (잠정 결정)               |
| 공유 영역 | `shared/`, AGENTS.md, lint 설정 변경은 작은 PR로 먼저 머지                 |

## 2. 하네스 개선 루프

에이전트가 같은 실수를 반복하면 **위에서부터** 고칠 위치를 고른다.

| 순서 | 위치             | 예                      |
| ---- | ---------------- | ----------------------- |
| 1    | lint·타입·테스트 | 커스텀 lint 규칙 추가   |
| 2    | 스크립트·스킬    | 반복 절차를 skill로     |
| 3    | `docs/rules/`    | 특정 영역 규칙 문서     |
| 4    | AGENTS.md        | 모든 작업에 해당할 때만 |

- PR 템플릿의 **"하네스 피드백"** 칸에 기록한다.
- **격주 15분 회고**에서 공유하고, 안 쓰는 규칙을 지운다.

## 3. 팀 설정 vs 개인 설정

| 커밋 (팀)                                                                     | 커밋 안 함 (개인)             |
| ----------------------------------------------------------------------------- | ----------------------------- |
| `AGENTS.md`, `CLAUDE.md`, `docs/rules/`                                       | `CLAUDE.local.md`             |
| `.agents/skills/`, `.claude/skills/`(링크), `tools/agent-hooks/`              | `.claude/settings.local.json` |
| `.claude/settings.json`, `.codex/hooks.json`, `lint-plugins/`, `lefthook.yml` | 개인 MCP 설정, 알림 훅        |
| `.vscode/extensions.json`, `.vscode/settings.json`                            | 개인 에디터 설정              |

- `pnpm add`·`pnpm remove`는 실행 전 확인을 받는다 (새 의존성 = ADR 대상).
- `.env*.local` 읽기는 막는다.

## 4. Claude와 Codex를 같이 쓸 때

Claude가 주력이고, 한도를 다 쓰면 Codex(GPT)로 넘어가는 상황을 기준으로 한다. GPT 쪽 도구는 Codex로 확정했다([개요](2026-11-22-harness-engineering-plan.md)의 잠정 결정 8번).

**지금 구조를 유지한다.** 하영님이 만든 `CLAUDE.md` = `@AGENTS.md` 구조는 Claude Code 공식 문서가 권장하는 방식과 같다.

| 파일        | 누가 읽나                                       | 역할                                  |
| ----------- | ----------------------------------------------- | ------------------------------------- |
| `AGENTS.md` | Codex는 바로 읽고, Claude는 `@AGENTS.md`로 읽음 | 규칙의 원본. 두 도구가 같은 내용을 봄 |
| `CLAUDE.md` | Claude만                                        | `@AGENTS.md` + Claude 전용 메모 몇 줄 |

> ⚠️ Claude Code는 `CLAUDE.md`가 있으면 `AGENTS.md`를 자동으로 읽지 않는다. 그래서 `@AGENTS.md` import가 꼭 필요하다(이미 되어 있음).

**도구별로 적용되는 것**

| 구성                                   | Claude Code      | GPT (Codex) | 비고                                                        |
| -------------------------------------- | ---------------- | ----------- | ----------------------------------------------------------- |
| `AGENTS.md`, `docs/`                   | ✅               | ✅          | 규칙의 원본                                                 |
| `CLAUDE.md`의 Claude 전용 메모         | ✅               | ❌          | 훅 안내만 둔다                                              |
| 스킬 (`.agents/skills`)                | ✅ (심볼릭 링크) | ✅          | [스킬·훅](2026-11-22-harness-engineering-4-skills-hooks.md) |
| `stop-gate` 훅 (검증 + 스킬 자동 요청) | ✅               | ✅          | 공용 스크립트                                               |
| `plan-gate`·포맷 훅, 권한 설정         | ✅               | ❌          | Claude 전용 (Codex는 `stop-gate`가 대신)                    |
| `pnpm verify`, lint, 테스트            | ✅               | ✅          | AGENTS.md "완료의 정의"로 요구                              |
| lefthook, CI                           | ✅               | ✅          | 도구와 무관한 최종 방어선                                   |

**규칙**

| 규칙                                                 | 이유                                                      |
| ---------------------------------------------------- | --------------------------------------------------------- |
| AGENTS.md에 Claude 전용 용어를 쓰지 않는다           | `/code-review` 같은 Claude 명령은 Codex가 읽으면 헷갈린다 |
| Claude 전용 내용은 `CLAUDE.md`의 `@AGENTS.md` 아래에 | Claude만 읽는다                                           |
| 스킬은 `.agents/skills` 한 곳에 둔다                 | 두 도구가 같은 스킬을 쓴다                                |
| 검증을 훅에만 맡기지 않는다                          | 훅이 없는 환경에서도 lefthook과 CI가 잡는다               |
