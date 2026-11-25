# FE 하네스 엔지니어링 도입 계획

- 상태: 완료
- 관련: [ADR 0002](../adr/0002-client-folder-structure.md) · [ADR 0003](../adr/0003-client-test-stack.md) · [ADR 0004](../adr/0004-agent-harness.md)
- 리뷰: 하영님 (아래 "잠정 결정"은 PR 리뷰에서 확정)

> 구현을 마쳤다. 리뷰를 위해 남겨 두었고, 리뷰가 끝나면 수명주기 규칙대로 이 문서와 주제별 문서를 함께 삭제한다. 확정된 내용은 ADR·rules·specs에 있다.

## 문서 구성

| 순서 | 문서                                                              | 내용                                                        |
| ---- | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| 0    | 이 문서                                                           | 요약, 한눈에 보기, 잠정 결정, 로드맵, 구현 위치             |
| 1    | [배경](2026-11-22-harness-engineering-1-background.md)            | 조사 요약, 현재 상태 진단, 설계 원칙, 참고 자료             |
| 2    | [가이드·센서](2026-11-22-harness-engineering-2-guides-sensors.md) | 검증 단계, lint, 폴더 구조, 테스트·브라우저 검증            |
| 3    | [협업·도구](2026-11-22-harness-engineering-3-collaboration.md)    | 작업 사이클, 하네스 개선 루프, 팀·개인 설정, Claude와 Codex |
| 4    | [스킬·훅](2026-11-22-harness-engineering-4-skills-hooks.md)       | 스킬·훅 통일 구조, 스킬 자동 적용, 외부 스킬                |

리뷰는 이 문서의 "한 장 요약"과 "잠정 결정"만 봐도 된다. 나머지는 근거와 세부 설계다.

## 한 장 요약

| 질문         | 답                                                                                                                                                 |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 하네스란?    | 에이전트에서 모델을 뺀 전부. 우리가 만드는 건 **가이드**(작업 전 안내)와 **센서**(작업 후 검사)                                                    |
| 지금 우리는? | 가이드 ✅ 탄탄함 / 센서 ❌ 거의 없음 (lint 규칙 2개, 테스트·CI·hook 0개)                                                                           |
| 핵심 제안 ①  | **`pnpm verify` 검증 단계**: 편집 직후 → 턴 종료 → 커밋 → PR마다 자동 검사                                                                         |
| 핵심 제안 ②  | **문서 규칙을 lint로**: 오류 메시지에 고치는 방법을 적어 에이전트가 스스로 고치게                                                                  |
| 핵심 제안 ③  | **실수 → 하네스 개선 루프**: 같은 실수가 두 번 나오면 규칙·센서를 고친다                                                                           |
| 도구 통일    | Claude 주력 + Codex 보조. 규칙(AGENTS.md)·스킬·훅을 한 벌로 두고 두 도구가 같이 쓴다 → [스킬·훅](2026-11-22-harness-engineering-4-skills-hooks.md) |
| 왜 지금?     | 코드 0줄. 폴더 구조와 의존 방향을 정하고 강제하기 가장 싼 시점                                                                                     |
| 얼마나 드나? | Phase 0 반나절 + Phase 1 하루. 나머지는 기능 개발과 함께                                                                                           |
| 결정 사항    | 8가지 모두 권장안으로 잠정 결정, PR 리뷰에서 의견 받기 → [잠정 결정](#잠정-결정)                                                                   |

## 한눈에 보기

| 영역   | 무엇                                                     | 왜                                       | Phase |
| ------ | -------------------------------------------------------- | ---------------------------------------- | ----- |
| 가이드 | AGENTS.md 재구성 (루트 + client)                         | 명령어·완료 정의·탐색 순서를 항상 읽히게 | 0     |
| 가이드 | Vite 템플릿 잔재 제거                                    | 나쁜 기존 패턴 복제 방지                 | 0     |
| 가이드 | 폴더 구조 + `specs/client-architecture.md`               | 의존 방향을 처음부터 고정                | 1     |
| 가이드 | `rules/` 추가 (testing, git-workflow 등)                 | 반복 참조하는 규칙 정리                  | 1~2   |
| 가이드 | plan 템플릿 = 진행 파일                                  | 세션이 끊겨도 이어받기                   | 1     |
| 가이드 | 스킬 통일(`.agents/skills`) + 팀 스킬 + 외부 FE 스킬 3개 | 반복 절차 자동화, 두 도구 공용           | 1~2   |
| 센서   | `typecheck`·`verify` 스크립트                            | 한 명령으로 pass/fail                    | 0     |
| 센서   | lint 강화 + 커스텀 규칙                                  | 문서 규칙을 기계로 강제                  | 0~1   |
| 센서   | 에이전트 훅 (`stop-gate`·`plan-gate` 등)                 | 검증 + 상황에 맞는 스킬 자동 요청        | 1     |
| 센서   | lefthook + GitHub Actions                                | 도구와 무관한 최종 방어선                | 1     |
| 센서   | Vitest + RTL + MSW                                       | 로직 검증, BE 없이 개발                  | 1     |
| 센서   | Playwright CLI 브라우저 검증                             | UI를 "사용자처럼" 확인                   | 2     |
| 센서   | `docs:check`                                             | 문서 정합성, ADR 번호 충돌               | 2     |
| 센서   | API 코드 생성 (BE 협의)                                  | BE 변경을 타입 오류로 감지               | 2     |
| 협업   | PR 템플릿 + 하네스 피드백 칸                             | 개선 루프를 습관으로                     | 0     |
| 협업   | 격주 15분 하네스 회고                                    | 규칙 가지치기, 개선 공유                 | 3     |

## 잠정 결정

> 8가지 모두 권장안으로 잠정 결정했다. 하영님은 PR 리뷰에서 다른 의견을 주면 되고, 합의된 항목은 `rules/`·`adr/`로 옮긴다.

| #   | 주제           | 잠정 결정                                                                                              | 다른 선택지                                                | 상태         |
| --- | -------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- | ------------ |
| 1   | 폴더 구조      | app · pages · features · shared                                                                        | FSD 전체                                                   | 리뷰 대기    |
| 2   | 테스트         | Vitest + RTL + MSW, E2E는 Phase 3                                                                      | E2E를 처음부터                                             | 리뷰 대기    |
| 3   | plan 수명주기  | 완료 PR에서 삭제 (git 이력이 보관소)                                                                   | `plans/done/`에 보관                                       | 리뷰 대기    |
| 4   | 브랜치·머지    | `main` 보호 + 상대방 승인 1명 필수 + squash merge                                                      | merge commit, 리뷰 선택                                    | 리뷰 대기    |
| 5   | AI 리뷰        | 작업이 끝나면 `stop-gate` 훅이 자동으로 독립 리뷰 요청 (변경분당 1회, `TTADAK_AUTO_SKILLS=0`으로 끄기) | 작성자가 수동 실행 / Claude GitHub App (조직 앱 설치 필요) | 리뷰 대기    |
| 6   | Stop hook 범위 | typecheck + lint + 관련 테스트 (느리면 lint만)                                                         | lint만                                                     | 리뷰 대기    |
| 7   | API 계약       | BE의 OpenAPI 스펙으로 타입·쿼리 훅·MSW 핸들러 생성                                                     | 수동 타입                                                  | BE 협의 필요 |
| 8   | GPT 쪽 도구    | Codex                                                                                                  | ChatGPT 웹 (레포의 AGENTS.md를 못 읽음)                    | 확정         |

## 로드맵

| Phase | 시점             | 할 일                                                                                                                             | ADR 후보               |
| ----- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **0** | 바로 (반나절)    | AGENTS.md 재구성 · `verify` 스크립트 · lint 강화 · 템플릿 잔재 제거 · PR 템플릿 · `.gitignore`                                    | —                      |
| **1** | 첫 기능 전 (1일) | 폴더 구조 + architecture lint · Vitest/RTL/MSW · lefthook · CI · 스킬·훅 통일(stop-gate, plan-gate, session-start) · git-workflow | 폴더 구조, 테스트 도구 |
| **2** | 첫 기능과 함께   | Playwright CLI 검증 · 외부 FE 스킬 · API 코드 생성 · `docs:check` · verify-ui·write-adr 스킬                                      | API 코드 생성          |
| **3** | 운영 중          | 격주 회고 · doc-garden 스킬 · knip · E2E · (Storybook)                                                                            | —                      |

<details>
<summary><b>Phase별 체크리스트 펼치기</b></summary>

**Phase 0**

- [x] 루트·client AGENTS.md 재구성, 탐색 순서를 AGENTS.md로 이동
- [x] `typecheck`, `verify:fast`, `verify` 스크립트
- [x] lint: 카테고리, restricted imports, `no-env-mode`, 타입 인식 규칙
- [x] Vite 템플릿 잔재 제거 (`App.tsx`, `App.css`, `index.css` 데모, `README.md`)
- [x] PR 템플릿, `.gitignore` 정리

**Phase 1**

- [x] 폴더 구조 결정 → `specs/client-architecture.md` + `ttadak/architecture`, `src/lib` 이동
- [x] Vitest + RTL + MSW, `rules/testing.md`
- [x] lefthook, GitHub Actions
- [x] 스킬·훅 통일 구조 (`.agents/skills`, `.claude/skills` 링크, `tools/agent-hooks`), `.claude/settings.json`·`.codex/hooks.json`
- [x] `stop-gate`(검증 + 스킬 자동 요청), `plan-gate`, `session-start` 훅, Vitest 세팅 후 `vitest related` 추가
- [x] `review-changes`·`new-feature` 스킬, `rules/code-review.md`
- [x] `rules/git-workflow.md`, plan 템플릿

**Phase 2**

- [x] Playwright CLI + `rules/ui-verification.md` + `verify-ui` 스킬
- [x] 외부 스킬 설치: playwright-cli, vercel-react-best-practices, web-design-guidelines
- [ ] BE와 API 계약 합의 → 코드 생성 + MSW (BE 스펙 필요, 후속)
- [x] `docs:check`, `write-adr` 스킬

**Phase 3**

- [ ] 격주 하네스 회고, `doc-garden` 스킬, knip
- [ ] 핵심 플로우 E2E, (디자인 시스템이 생기면) Storybook·디자인 토큰 lint

</details>

## 하지 않을 것

| ❌ 하지 않을 것                       | 이유                                     |
| ------------------------------------- | ---------------------------------------- |
| LLM으로 AGENTS.md 생성 후 그대로 커밋 | 성능은 떨어지고 비용은 늘었다 (ETH 연구) |
| AGENTS.md에 코드 스타일 나열          | Prettier·oxlint의 일                     |
| 하네스를 미리 전부 구축               | 실패를 관찰한 뒤에 추가한다              |
| 증거 없는 "완료했습니다" 수용         | 명령과 출력, 스크린샷을 요구한다         |
| Spec Kit 등 무거운 SDD 도구           | 지금 문서 체계로 충분하다                |

## 구현 위치

부록에 있던 초안은 실제 파일로 옮겼다. 아래 파일이 원본이고, 이 문서보다 우선한다.

| 항목               | 파일                                                                                                    |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| 루트 지도          | `AGENTS.md`, `CLAUDE.md`                                                                                |
| client 규칙        | `client/AGENTS.md`, `client/CLAUDE.md`                                                                  |
| 폴더 구조          | `client/docs/specs/client-architecture.md`                                                              |
| 도구·스크립트·환경 | `client/docs/specs/client-tooling.md`, `client/package.json`                                            |
| lint               | `client/.oxlintrc.json`, `client/lint-plugins/ttadak.js`                                                |
| 테스트             | `client/vite.config.ts`의 `test`, `client/src/test/`, `client/.env.test`                                |
| rules              | `client/docs/rules/` (testing, code-review, ui-verification, git-workflow), plan 템플릿은 documentation |
| ADR                | `client/docs/adr/0002`~`0004`                                                                           |
| 에이전트 훅        | `tools/agent-hooks/`, `.claude/settings.json`, `.codex/hooks.json`                                      |
| 스킬               | `.agents/skills/`, `.claude/skills/`(링크), `skills-lock.json`                                          |
| git hook           | `lefthook.yml`, `client/scripts/check-commit-msg.mjs`                                                   |
| CI                 | `.github/workflows/client.yml`                                                                          |
| 문서 검사          | `client/scripts/check-docs.mjs`                                                                         |
| PR 템플릿          | `.github/pull_request_template.md`                                                                      |
