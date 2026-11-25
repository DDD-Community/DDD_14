# FE 하네스: 가이드와 센서

- 상태: 완료
- 상위 문서: [개요](2026-11-22-harness-engineering-plan.md)

## 1. 검증 단계

| 시점             | 실행                          | 하는 일                                                                    | 목표 시간       |
| ---------------- | ----------------------------- | -------------------------------------------------------------------------- | --------------- |
| ① 파일 편집 직후 | Claude Code `PostToolUse`     | 그 파일만 Prettier + `oxlint --fix`                                        | < 2초           |
| ② 턴 종료        | `Stop` 훅 (Claude·Codex)      | `verify:fast` → 통과하면 필요한 스킬(plan, 화면 확인, ADR, 리뷰) 자동 요청 | < 15초 (+ 스킬) |
| ③ 커밋           | lefthook                      | staged 파일 lint·format, 커밋 메시지 형식                                  | < 5초           |
| ④ PR             | GitHub Actions                | `pnpm verify` 전체 + `docs:check`                                          | < 3분           |
| ⑤ 리뷰           | 자동 AI 리뷰(②) → 상대방 리뷰 | spec 일치, 테스트 의도, 설계                                               | —               |

> 💡 성공하면 조용히, 실패하면 짧게. 에이전트 컨텍스트를 아낀다.

> 💡 자동 리뷰 등 스킬 실행은 사용량을 쓴다. 같은 변경에는 한 번만 요청하고, 한도가 빠듯할 땐 `TTADAK_AUTO_SKILLS=0`으로 끈다.

**스크립트**

```jsonc
"typecheck": "tsc -b",
"test": "vitest run",
"test:watch": "vitest",
"verify:fast": "pnpm typecheck && pnpm lint",
"verify": "pnpm typecheck && pnpm lint && pnpm format:check && pnpm test && vite build",
"docs:check": "node scripts/check-docs.mjs"
```

## 2. lint 강화 (oxlint 유지, ADR 0001대로)

| 규칙                                           | 막는 것                                       |
| ---------------------------------------------- | --------------------------------------------- |
| `categories: correctness`                      | 확실한 버그 패턴 (error)                      |
| `typescript/no-floating-promises`              | 처리 안 된 Promise (TanStack Query·axios)     |
| `no-restricted-imports`                        | axios·clsx·tailwind-merge 직접 import, `../`  |
| `ttadak/no-env-mode` (커스텀)                  | `import.meta.env.MODE`·`PROD`·`DEV`           |
| `ttadak/architecture` (커스텀)                 | 레이어 역방향, feature 간 import, deep import |
| `vitest/no-disabled-tests`, `no-focused-tests` | 테스트 skip·only로 통과시키기                 |
| `import/no-cycle`                              | 순환 의존                                     |

**메시지 예시** — 무엇이 틀렸는지 + 고치는 법 + 근거 문서

```text
features/auth에서 features/feed를 import할 수 없습니다.
pages/에서 조립하거나 공통 코드는 shared/로 옮기세요. (docs/specs/client-architecture.md)
```

> ⚠️ oxlint JS 플러그인은 아직 알파(2026-03)다. 문제가 생기면 dependency-cruiser로 대체할 수 있다.

## 3. 폴더 구조 (잠정 결정)

```text
src/
├─ app/        진입점, Provider, 라우터
├─ pages/      라우트 단위 화면 (features를 조립만)
├─ features/   기능 단위, index.ts로 공개 API만 노출
│  └─ <name>/  components/ hooks/ api/ model/ index.ts
└─ shared/     도메인 무관: ui/ lib/ hooks/ config/
```

| 규칙              | 내용                                             |
| ----------------- | ------------------------------------------------ |
| 의존 방향         | `app → pages → features → shared` (역방향 금지)  |
| feature 간 import | 금지. pages에서 조립하거나 shared로 옮긴다       |
| feature 공개 API  | 밖에서는 `@/features/<name>`(index.ts)만 import  |
| 기존 코드         | `src/lib/*` → `src/shared/lib/*` 이동, spec 갱신 |

- FSD를 단순화한 형태다. FSD 전체(entities, widgets 등)는 2인 단기 프로젝트에 무겁다고 판단했다.

## 4. 테스트와 브라우저 검증

| 대상                      | 방법                           | 기준                         |
| ------------------------- | ------------------------------ | ---------------------------- |
| 훅·유틸·상태 로직·폼 검증 | Vitest                         | 필수. **테스트 먼저** 작성   |
| 컴포넌트                  | React Testing Library          | 핵심만, 사용자 행동 단위     |
| API                       | MSW                            | BE 완성 전에도 개발·테스트   |
| 화면·시각 디테일          | Playwright CLI (에이전트 도구) | UI 변경 PR에 스크린샷 첨부   |
| 핵심 플로우 2~3개         | Playwright E2E                 | Phase 3                      |
| 컴포넌트 카탈로그         | Storybook                      | 선택. 디자인 시스템이 생기면 |

> 💡 리뷰어는 구현보다 **테스트를 먼저** 본다. 테스트가 곧 스펙이다.
