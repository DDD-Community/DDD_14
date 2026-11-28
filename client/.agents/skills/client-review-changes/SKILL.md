---
name: client-review-changes
description: 이번 변경(git diff)을 독립 리뷰한다. stop-gate 훅이 리뷰를 요청했을 때나 PR을 만들기 전에 쓴다.
---

# 변경분 독립 리뷰

1. 새 서브에이전트를 만들어 리뷰를 맡긴다. 직접 다시 읽는 것으로 대신하지 않는다. 만든 쪽은 자기 코드에 관대하다.
2. 서브에이전트에게 줄 지시:
   - `git diff HEAD -- client`와 새 파일(`git status --short client`)을 읽는다.
   - `client/docs/rules/code-review.md` 체크리스트로 검사한다. 화면 변경이 있으면 web-design-guidelines 스킬(`client/.agents/skills/web-design-guidelines/SKILL.md`) 기준도 본다.
   - 결과를 `[필수]`와 `[권장]`으로 나눠 `파일:줄`과 함께 짧게 보고한다. 문제가 없으면 "지적 없음". 코드는 고치지 않는다.
3. `[필수]`는 고치고, 고치지 않은 지적은 이유를 한 줄로 남긴다.
4. 보고에 리뷰 요약(지적 수, 수정 수)을 포함한다.
