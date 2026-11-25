---
name: new-feature
description: client에 기능을 추가하거나 동작을 바꿀 때 쓴다. "~ 만들어줘", "~ 추가해줘", "~ 구현해줘" 같은 요청이나, plan-gate·stop-gate 훅이 요청했을 때 쓴다.
---

# 기능 구현 절차

1. plan: `client/docs/plans/YYYY-MM-DD-<topic>-plan.md`를 `client/docs/rules/documentation.md`의 plan 템플릿대로 쓴다(`- 상태: 진행 중`). 작은 수정이면 목표와 단계 몇 줄이면 된다.
2. 읽기: `client/AGENTS.md` 문서 지도 순서대로 관련 `rules/` → `specs/` → `adr/`를 읽는다. 폴더 위치는 `specs/client-architecture.md`를 따른다.
3. 테스트 먼저: 로직(훅, 유틸, 상태, 폼 검증)은 실패하는 테스트부터 쓴다. 규칙은 `rules/testing.md`.
4. 구현: 한 번에 하나의 슬라이스만. React 코드는 vercel-react-best-practices 스킬 기준을 따른다.
5. 검증: `client/`에서 `pnpm verify`. 화면을 바꿨으면 verify-ui 스킬을 쓴다.
6. 문서: 동작이 바뀌었으면 spec을 갱신하고, 큰 결정이나 새 의존성이면 write-adr 스킬을 쓴다.
7. 마무리: plan의 체크리스트와 진행 로그를 갱신하고, `.github/pull_request_template.md` 형식으로 PR 본문 초안을 쓴다.
