---
name: client-verify-ui
description: client 화면(.tsx, .css)을 바꾼 뒤 브라우저에서 확인할 때 쓴다. stop-gate 훅이 요청했을 때도 쓴다.
---

# 화면 확인 절차

규칙과 확인 항목은 `client/docs/rules/ui-verification.md`에 있다.

1. `client/`에서 `pnpm dev`를 백그라운드로 띄운다(http://localhost:5173). 이미 떠 있으면 그대로 쓴다.
2. playwright-cli 스킬(`client/.agents/skills/playwright-cli/SKILL.md`)에 따라 `pnpm exec playwright-cli`로 바뀐 화면을 연다. 사용자처럼 클릭하고 입력해서 바뀐 동작을 확인한다. 브라우저가 없다는 오류가 나면 `pnpm exec playwright-cli install-browser`를 먼저 실행한다.
3. `playwright-cli console`로 콘솔 에러가 없는지 확인한다.
4. 좁은 화면도 본다: `playwright-cli resize 390 844`.
5. 스크린샷을 `client/.screenshots/`에 저장하고 보고에 경로를 남긴다. PR에 첨부한다.
