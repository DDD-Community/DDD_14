# 타닥 (TTADAK)

DDD 14기 프로젝트 모노레포. 이 파일은 어느 작업이 어느 폴더와 하네스를 따르는지만 정한다.

## 백엔드 개발 → `server/`

- 세션은 **`server/`에서 시작**한다.
- **`server/AGENTS.md`와 server 하네스만 따른다.** server 하네스는 `server/.claude/`(훅·스킬·에이전트)와 `server/docs/`이며, 자세한 안내는 `server/AGENTS.md`에 있다.
- 이 파일과 루트·`client/`의 하네스는 백엔드 작업에 적용되지 않는다. **단, 아래 "함께 지키는 것"은 백엔드도 따른다.**

## 프론트엔드 개발 → 레포 루트에서 시작, `client/` 규칙

- 세션은 **레포 루트에서 시작**한다. 서버 코드도 함께 참고할 수 있다.
- **`client/AGENTS.md`와 client 하네스를 따른다.** client 하네스는 `client/.agents/skills/`(스킬)와 `client/scripts/agent-hooks/`(훅)이며, 루트 `.claude/settings.json`·`.codex/hooks.json`은 이 훅을 등록만 한다.
- `server/`의 코드와 문서는 참고만 한다. `server/`의 작업 절차(일지, 슬라이스 등)는 따르지 않고, 사용자가 시키지 않으면 `server/` 파일을 고치지 않는다.

## 함께 지키는 것

FE·BE 모두 같은 규칙과 템플릿을 쓴다. 절차(스킬)는 각 영역 하네스에 있다.

| 항목        | 기준                                             |
| ----------- | ------------------------------------------------ |
| 브랜치·커밋 | `client/docs/rules/git-workflow.md`              |
| PR          | `.github/pull_request_template.md`, squash merge |
| 이슈        | `.github/ISSUE_TEMPLATE/`                        |
| AI 금지     | PR 병합, `main` push, force push                 |
