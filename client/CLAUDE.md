@AGENTS.md

## Claude Code 전용

- 파일을 고치면 훅이 Prettier와 oxlint를 자동으로 실행한다. 진행 중인 plan 없이 `src/`를 고치려 하면 훅이 막는다.
- 끝내려 할 때 훅이 `verify:fast`를 돌리고, 필요한 스킬(plan, 화면 확인, ADR, 리뷰)을 요청한다. 그대로 따르고, 리뷰는 반드시 서브에이전트에게 맡긴다.
