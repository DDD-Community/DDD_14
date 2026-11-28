---
name: client-write-adr
description: 기술 선택이나 구조 결정을 ADR로 기록할 때 쓴다. 새 의존성을 추가했거나 spec을 크게 바꿨을 때, stop-gate 훅이 요청했을 때 쓴다.
---

# ADR 작성 절차

1. `client/docs/rules/documentation.md`의 `adr/` 규칙을 읽는다.
2. 번호: `client/docs/adr/`에서 가장 큰 번호에 1을 더한다(4자리). 파일명은 `NNNN-<주제>.md`.
3. 구조: `# NNNN. 주제` / 상태 / 배경 / 결정(채택 이유, 고려한 대안과 장단점) / 결과.
4. 상태는 처음에 `제안됨 (Proposed)`. PR 리뷰에서 수락되면 `수락됨 (Accepted)`으로 바꾼다.
5. 기존 결정을 바꾸면 원래 ADR의 상태를 `대체됨 (Superseded)`으로 바꾸고 새 ADR에서 참조한다. 덮어쓰지 않는다.
6. 관련 spec의 변경 이력에 한 줄과 ADR 링크를 남긴다.
7. `client/`에서 `pnpm docs:check`로 번호와 링크를 확인한다.
