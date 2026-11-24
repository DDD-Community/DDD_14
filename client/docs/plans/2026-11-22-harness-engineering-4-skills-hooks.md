# FE 하네스: 스킬과 훅 (Claude·Codex 통일)

- 상태: 완료
- 상위 문서: [개요](2026-11-22-harness-engineering-plan.md)

## 1. 통일 구조

원본은 한 곳에 두고, 도구별 위치는 링크나 등록 파일로만 연결한다.

```text
.agents/skills/<name>/SKILL.md   스킬 원본. Codex가 바로 읽는다
.claude/skills/<name>            → ../../.agents/skills/<name> 심볼릭 링크 (Claude Code용)
tools/agent-hooks/*.mjs          훅 스크립트 원본 (공용)
.claude/settings.json            Claude Code에 훅·권한 등록
.codex/hooks.json                Codex에 훅 등록
```

| 사실                                                               | 그래서                                              |
| ------------------------------------------------------------------ | --------------------------------------------------- |
| 두 도구 모두 Agent Skills 표준(`SKILL.md`)을 쓴다                  | 스킬 파일 하나로 두 도구가 같이 쓴다                |
| Codex는 `.agents/skills`, Claude Code는 `.claude/skills`를 읽는다  | 원본은 `.agents/skills`, Claude 쪽은 심볼릭 링크    |
| Claude Code는 심볼릭 링크로 된 스킬 폴더를 지원한다                | 복사본 없이 한 벌만 관리                            |
| `npx skills add`(Vercel skills CLI)가 기본으로 이 구조로 설치한다  | 외부 스킬도 같은 구조로 들어온다                    |
| Claude 전용 frontmatter(`context: fork` 등)는 다른 도구가 무시한다 | 공용 스킬은 표준 필드(`name`, `description`)만 쓴다 |

> ⚠️ 외부 스킬에는 스크립트가 들어 있을 수 있다. 설치한 스킬도 커밋해서 PR에서 내용을 리뷰한다. 스킬 설명은 매 세션 컨텍스트에 올라가므로 전체 10개 이하로 유지한다.

## 2. 외부 FE 스킬 검토

| 스킬                          | 만든 곳          | 하는 일                                          | 판단    | 이유                                                         |
| ----------------------------- | ---------------- | ------------------------------------------------ | ------- | ------------------------------------------------------------ |
| `playwright-cli`              | Microsoft (공식) | 브라우저 열기·클릭·스크린샷 명령 레퍼런스        | ✅ 채택 | UI 검증의 핵심 센서. `verify-ui`가 이 스킬을 쓴다            |
| `vercel-react-best-practices` | Vercel Labs      | React 성능 규칙 (요청 워터폴, 번들 크기, 리렌더) | ✅ 채택 | 에이전트가 자주 만드는 성능 실수 예방. 서버 전용 규칙은 무시 |
| `web-design-guidelines`       | Vercel Labs      | 접근성·UX 가이드라인 기준으로 UI 코드 리뷰       | ✅ 채택 | 자동 리뷰에서 UI 변경 점검에 쓴다                            |
| `frontend-design`             | Anthropic        | 독창적인 디자인 방향 제시                        | ❌ 보류 | 디자이너 시안을 구현하는 팀이라 맞지 않는다                  |

- TanStack Query·Tailwind 공식 스킬은 이번 조사에서 확인하지 못했다. 필요하면 `rules/api-call.md` 같은 우리 규칙으로 대신한다.

## 3. 팀 스킬 (우리가 직접 만드는 것)

| 스킬             | 언제 쓰나                      | 하는 일                                                                                       | Phase |
| ---------------- | ------------------------------ | --------------------------------------------------------------------------------------------- | ----- |
| `new-feature`    | 기능 구현을 시작할 때          | plan 작성 → spec·adr 읽기 → 테스트 먼저 → 구현 → verify → 브라우저 확인 → 문서 갱신 → PR 초안 | 1     |
| `review-changes` | `stop-gate`가 리뷰를 요청할 때 | 서브에이전트에게 diff + `rules/code-review.md` 체크리스트로 리뷰를 맡기고 지적 반영           | 1     |
| `verify-ui`      | UI를 바꿨을 때                 | dev 서버 실행 → `playwright-cli`로 화면 확인, 스크린샷, 콘솔 에러 확인                        | 2     |
| `write-adr`      | 기술 결정을 기록할 때          | 다음 번호 계산 → ADR 표준 구조 → spec 변경 로그 연결                                          | 2     |
| `doc-garden`     | 스프린트 끝                    | `specs/`와 코드가 어긋난 곳을 찾아 고친다                                                     | 3     |

## 4. 스킬을 자동으로 적용하는 방법

스킬은 에이전트가 요청 내용을 보고 고르는 것이라 그대로 두면 확률적이다. 그래서 **훅이 "스킬이 필요한 상황"을 감지해서 그 스킬을 실행하라고 요구**하게 만든다. 훅은 항상 돌기 때문에 스킬을 쓰라는 요청도 항상 나온다.

| 스킬             | 훅이 감지하는 상황                              | 훅                                   | 시점           |
| ---------------- | ----------------------------------------------- | ------------------------------------ | -------------- |
| `new-feature`    | 진행 중인 plan 없이 `client/src`를 고치려 함    | `plan-gate` (Claude)                 | 편집 **전**    |
| `new-feature`    | `client/src`가 바뀌었는데 진행 중인 plan이 없음 | `stop-gate` (공용, Codex는 이것으로) | 작업 종료 시   |
| `verify-ui`      | 화면 파일(`.tsx`, `.css`)이 새로 바뀜           | `stop-gate`                          | 작업 종료 시   |
| `write-adr`      | `package.json`에 새 의존성이 생김               | `stop-gate`                          | 작업 종료 시   |
| `review-changes` | client 변경이 있음                              | `stop-gate`                          | 작업 종료 시   |
| 외부 스킬 3개    | 위 팀 스킬이 실행될 때                          | 팀 스킬 본문에서 명시적으로 호출     | 팀 스킬 안에서 |
| `doc-garden`     | 시간 기준 (스프린트 끝)                         | 예약 작업 또는 수동                  | 주기적         |

- 외부 스킬은 팀 스킬 안에서 부른다. `new-feature`는 vercel-react-best-practices를, `verify-ui`는 playwright-cli를, `review-changes`는 web-design-guidelines를 부른다. 이렇게 하면 "훅 → 팀 스킬 → 외부 스킬"로 이어져서 모두 자동으로 적용된다.
- `stop-gate`는 필요한 스킬을 한 번에 모아서 요청하고, 같은 변경에는 다시 요청하지 않는다. 화면이 그대로면 verify-ui를, 이미 기록한 의존성이면 write-adr를 다시 요청하지 않는다.
- `plan-gate`는 하영님이 만든 "구현 전에 plan을 먼저 쓴다" 규칙을 기계적으로 강제하는 것이다.
- 한계: 스킬을 쓰라는 **요청**은 보장되지만, 스킬을 얼마나 성실히 수행하는지는 에이전트에게 달려 있다. 결과는 lefthook, CI, 사람 리뷰가 한 번 더 본다.
- 끄는 법: 스킬 요청 전체는 `TTADAK_AUTO_SKILLS=0`(검증은 계속 돈다), plan 강제는 `TTADAK_PLAN_GATE=0`, `stop-gate` 전체는 `TTADAK_STOP_GATE=0`. 검증이 같은 작업에서 3번 넘게 실패하면 더 막지 않는다.
- 검토했지만 택하지 않은 방법: 매 프롬프트마다 키워드로 요청을 분류해 스킬을 붙이는 `UserPromptSubmit` 훅. 키워드 분류가 불안정하고 매번 컨텍스트를 쓴다.

## 5. 훅

| 훅                   | 이벤트                   | 하는 일                                                                  | Claude    | Codex                                      | Phase              |
| -------------------- | ------------------------ | ------------------------------------------------------------------------ | --------- | ------------------------------------------ | ------------------ |
| `stop-gate`          | Stop                     | `verify:fast` → 통과하면 변경 내용에 맞는 스킬을 모아서 요청             | ✅        | ✅ (출력 형식은 도입 시 확인)              | 1                  |
| `plan-gate`          | PreToolUse (Edit·Write)  | 진행 중인 plan 없이 `client/src`를 고치려 하면 막고 `new-feature`로 안내 | ✅        | ❌ (`stop-gate`가 사후에 대신)             | 1                  |
| `session-start`      | SessionStart             | 진행 중인 plan을 알려 줘서 새 세션이 이어서 작업하게 한다                | ✅        | 확인 필요                                  | 1                  |
| `format-edited-file` | PostToolUse (Edit·Write) | 고친 파일만 Prettier + `oxlint --fix`                                    | ✅        | ❌ 편집 방식이 달라 보류 (lefthook이 대신) | 1                  |
| `stop-gate` 확장     | Stop                     | 바뀐 파일과 관련된 테스트만 `vitest related`로 실행                      | ✅        | ✅                                         | 1 (Vitest 세팅 후) |
| 알림                 | Notification             | 에이전트가 입력을 기다릴 때 데스크톱 알림                                | 개인 설정 | —                                          | 선택               |

## 6. 권한 (훅 없이 설정만으로 막는 것, Claude)

| 막을 것                      | 설정                                          | Codex 쪽 대안                     |
| ---------------------------- | --------------------------------------------- | --------------------------------- |
| 새 의존성 추가               | `pnpm add`·`pnpm remove` → 실행 전 확인       | AGENTS.md 규칙 + PR 리뷰          |
| lint 규칙 완화               | `.oxlintrc.json`, `lint-plugins/` 수정 → 확인 | PR 리뷰                           |
| lockfile·생성 코드 직접 수정 | 수정 금지                                     | CI에서 "재생성 후 diff 없음" 검사 |
| 개인 env 파일                | `.env*.local` 읽기 금지                       | —                                 |
