# FE 하네스: 배경 (조사·진단·원칙)

- 상태: 완료
- 상위 문서: [개요](2026-11-22-harness-engineering-plan.md)

## 1. 조사 요약

### 1.1 하네스의 세 겹 (Böckeler)

| 계층              | 예                                       | 만드는 사람 |
| ----------------- | ---------------------------------------- | ----------- |
| 모델              | Claude, GPT                              | 모델 제공사 |
| 도구 하네스       | Claude Code, Codex, Cursor               | 도구 제작사 |
| **사용자 하네스** | AGENTS.md, rules, lint, 테스트, hook, CI | **우리**    |

### 1.2 가이드 × 센서

|                      | 계산적 (결정론적, 빠르고 쌈) | 추론적 (LLM 기반)        |
| -------------------- | ---------------------------- | ------------------------ |
| **가이드** (작업 전) | 타입, 코드 생성기, 템플릿    | AGENTS.md, rules, skills |
| **센서** (작업 후)   | tsc, lint, 테스트            | AI 코드 리뷰             |

> 💡 "CLAUDE.md의 한 줄을 계속 강조해도 놓친다면, 그 줄은 hook으로 옮겨야 한다." (Claude Code 공식 문서)

### 1.3 핵심 원칙 9가지

| #   | 원칙                       | 한 줄 요약                                                                              | 출처                    |
| --- | -------------------------- | --------------------------------------------------------------------------------------- | ----------------------- |
| 1   | AGENTS.md는 지도           | 약 100줄 지도 + 자세한 건 `docs/`. LLM이 생성한 파일은 성공률 -3%, 비용 +20%            | OpenAI, ETH Zurich      |
| 2   | 반복해서 놓치면 센서로     | 문서에서 강조하는 대신 lint·hook으로 강제                                               | Böckeler, Claude Code   |
| 3   | 오류 메시지 = 수정 지침    | lint 메시지에 고치는 법을 적는다. 에이전트는 기존 패턴(나쁜 것 포함)을 그대로 따라 한다 | OpenAI                  |
| 4   | pass/fail 수단을 준다      | 검증 수단이 있으면 품질 2~3배. UI는 브라우저에서 "사용자처럼" 확인                      | Boris Cherny, Anthropic |
| 5   | 만든 쪽이 채점하지 않는다  | 자기 평가는 관대하다. 테스트를 지우거나 skip하는 "치팅"을 감시                          | Anthropic, Kent Beck    |
| 6   | 실수 → 하네스 개선         | 실수할 때마다 재발 방지 장치를 만든다. 실패를 본 뒤에 추가한다                          | Hashimoto               |
| 7   | 작게 나누고, 상태는 파일로 | 한 세션에 기능 하나. 진행 파일 + 커밋으로 다음 세션이 이어받는다                        | Anthropic               |
| 8   | 엔트로피 관리              | 코드와 어긋난 문서를 주기적으로 찾아 고친다                                             | OpenAI                  |
| 9   | 하네스는 "가정"이다        | 모델이 바뀌면 다시 보고 걷어낸다. 요구사항을 제대로 이해했는지는 사람이 확인한다        | Anthropic, Böckeler     |

### 1.4 스펙 주도 개발(SDD)은?

- 우리 `docs/specs/`(코드와 일치해야 하는 source of truth)는 이미 **spec-anchored** 방식이다.
- Spec Kit 같은 별도 도구는 **도입하지 않는다**. 지금 문서 체계에 센서를 붙이는 게 더 이득이다.

## 2. 현재 상태 진단

### 2.1 스코어카드

| 영역   | 항목                              | 상태 | 메모                                                      |
| ------ | --------------------------------- | ---- | --------------------------------------------------------- |
| 가이드 | 문서 체계 (rules/specs/adr/plans) | ✅   | OpenAI 구조와 거의 같다. 그대로 살린다                    |
| 가이드 | AI 탐색 순서                      | ⚠️   | `documentation.md`에만 있어서 구현 중에는 안 읽힐 수 있다 |
| 가이드 | 명령어·완료 정의                  | ❌   | AGENTS.md에 없다 (spec에만 있음)                          |
| 가이드 | 루트 AGENTS.md                    | ❌   | 비어 있다                                                 |
| 가이드 | Vite 템플릿 잔재                  | ⚠️   | 에이전트가 데모 코드를 "기존 패턴"으로 따라 할 수 있다    |
| 센서   | 타입 체크                         | ⚠️   | `build`에 묶여 있고 단독 스크립트가 없다                  |
| 센서   | lint                              | ⚠️   | 기본 규칙 + 규칙 2개                                      |
| 센서   | 테스트                            | ❌   | 없음                                                      |
| 센서   | git hook / CI                     | ❌   | 없음                                                      |
| 센서   | 에이전트 hook                     | ❌   | 없음                                                      |
| 센서   | 브라우저 검증                     | ❌   | 없음                                                      |

### 2.2 문서 규칙 vs 실제 강제 (`specs/client-tooling.md`)

| 규칙                                           | 강제되나 | 제안                                       |
| ---------------------------------------------- | -------- | ------------------------------------------ |
| HTTP 요청은 `api` 인스턴스로만                 | ❌       | lint: axios 직접 import 금지               |
| className은 `cn()`으로만                       | ❌       | lint: clsx·tailwind-merge 직접 import 금지 |
| 환경 분기는 `VITE_APP_ENV`, `MODE`·`PROD` 금지 | ❌       | 커스텀 lint `ttadak/no-env-mode`           |
| 새 env 변수는 `vite-env.d.ts`에 타입 추가      | ❌       | `docs:check` 스크립트로 대조               |
| 서버 데이터를 zustand에 복사 금지              | ❌       | AI 리뷰 체크리스트 (기계화 어려움)         |

### 2.3 2인 협업 리스크

| 리스크                | 상황                                                   | 대응                                                                                                       |
| --------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| ADR 번호 충돌         | 두 사람이 각자 브랜치에서 `0002-*.md` 작성             | 나중에 머지하는 쪽이 번호 변경 + CI 검사                                                                   |
| plan 수명주기 미정    | 끝난 plan을 에이전트가 현재 계획으로 오해              | 완료 PR에서 plan 삭제 (잠정 결정)                                                                          |
| 하네스 설정 drift     | 각자 로컬 설정이 달라 에이전트가 다르게 움직임         | 팀 설정은 커밋, 개인 설정은 `*.local`                                                                      |
| 에디터 설정 공유 불가 | 루트 `.gitignore`의 `.vscode`가 예외 규칙을 무력화     | `.gitignore` 정리                                                                                          |
| 도구 전환             | Claude가 주력이지만 한도를 다 쓰면 GPT로 작업하기도 함 | 원본은 AGENTS.md, 최종 강제는 git hook·CI → [협업·도구](2026-11-22-harness-engineering-3-collaboration.md) |

## 3. 설계 원칙

| #   | 원칙                                 | 의미                                            |
| --- | ------------------------------------ | ----------------------------------------------- |
| 1   | **AGENTS.md는 지도, `docs/`는 원본** | AGENTS.md에는 명령어·완료 정의·문서 지도만      |
| 2   | **두 번 지적하면 센서로**            | 먼저 lint·테스트·hook으로 막을 수 있는지 본다   |
| 3   | **모든 작업은 pass/fail로 끝난다**   | `pnpm verify` 통과 + UI는 브라우저 확인 증거    |
| 4   | **최종 방어선은 결정론적 검사**      | 에이전트 hook은 편의, 최종 강제는 git hook + CI |
| 5   | **하네스도 코드다**                  | 팀 설정은 커밋·리뷰                             |
| 6   | **작게 시작해서 키운다**             | 실제로 관찰한 실패에 맞춰 추가                  |

## 참고 자료

| 구분 | 자료                                                                                                                                                                                                                         | 이 문서에서 쓴 내용                              |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| 요약 | OpenAI, [Harness engineering](https://openai.com/index/harness-engineering/) (2026-02)                                                                                                                                       | 지도형 AGENTS.md, 커스텀 lint, doc-gardening     |
| 요약 | Böckeler, [Harness engineering for coding agent users](https://martinfowler.com/articles/harness-engineering.html) / [first thoughts](https://www.martinfowler.com/articles/exploring-gen-ai/harness-engineering-memo.html)  | 세 겹 구조, 가이드×센서                          |
| 요약 | Hashimoto, [My AI Adoption Journey](https://mitchellh.com/writing/my-ai-adoption-journey) (2026-02)                                                                                                                          | 실수 → 하네스 개선                               |
| 원문 | Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11)                                                                        | 진행 파일, 한 번에 기능 하나                     |
| 원문 | Anthropic, [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) (2026-03)                                                                                          | 생성자·평가자 분리                               |
| 원문 | [Claude Code Best practices](https://code.claude.com/docs/en/best-practices)                                                                                                                                                 | pass/fail 검증, hook으로 옮기기                  |
| 원문 | [Claude Code 메모리 문서 (CLAUDE.md·AGENTS.md)](https://code.claude.com/docs/en/memory)                                                                                                                                      | `@AGENTS.md` import, 하위 디렉터리 로딩          |
| 원문 | [Claude Code hooks](https://code.claude.com/docs/en/hooks) / [skills](https://code.claude.com/docs/en/skills)                                                                                                                | Stop 훅 차단·루프 방지, 스킬 위치·심볼릭 링크    |
| 요약 | OpenAI, [Codex skills](https://developers.openai.com/codex/skills) / [Codex hooks](https://developers.openai.com/codex/hooks)                                                                                                | `.agents/skills`, `.codex/hooks.json`            |
| 요약 | [Agent Skills 표준](https://agentskills.io/) / [Vercel skills CLI](https://www.mintlify.com/vercel-labs/skills)                                                                                                              | SKILL.md 공용 포맷, `.agents/skills` + 링크 설치 |
| 요약 | [vercel-labs/agent-skills](https://tessl.io/registry/skills/github/vercel-labs/agent-skills) / [Playwright CLI skills](https://playwright.dev/agent-cli/skills) / [skills.sh React](https://skills.sh/topic/react)           | 외부 FE 스킬                                     |
| 요약 | HumanLayer, [Writing a good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) / [Skill Issue](https://humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents)                              | 짧은 루트 파일, 조용한 성공 출력                 |
| 요약 | ETH Zurich, [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) (ICLR 2026)                                                                                                                                             | LLM 생성 컨텍스트 파일의 효과                    |
| 요약 | [Boris Cherny 워크플로 (InfoQ)](https://www.infoq.com/news/2026/01/claude-code-creator-workflow)                                                                                                                             | 검증으로 품질 2~3배, format hook                 |
| 요약 | Kent Beck, [Augmented Coding](https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes)                                                                                                                           | 테스트 치팅 감시, TDD                            |
| 요약 | Böckeler, [SDD 도구 비교](https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) / Marmelab, [Waterfall Strikes Back](https://marmelab.com/blog/2025/11/12/spec-driven-development-waterfall-strikes-back) | spec-anchored, SDD 비판                          |
| 요약 | [Oxlint JS Plugins Alpha](https://oxc.rs/blog/2026-03-11-oxlint-js-plugins-alpha) / [Playwright CLI](https://playwright.dev/agent-cli/introduction)                                                                          | 도구 현황                                        |

> "원문"은 본문을 직접 읽은 자료, "요약"은 네트워크 정책 때문에 본문을 열지 못해 검색 결과와 2차 요약으로 확인한 자료다.
