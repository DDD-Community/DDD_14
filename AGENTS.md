# 타닥 (TTADAK)

DDD 14기 프로젝트 모노레포.

| 경로      | 내용                              | 가이드                               |
| --------- | --------------------------------- | ------------------------------------ |
| `client/` | 웹 프론트엔드 (React + TS + Vite) | [client/AGENTS.md](client/AGENTS.md) |
| `server/` | 백엔드                            | [server/AGENTS.md](server/AGENTS.md) |

- 작업하는 디렉터리의 AGENTS.md를 먼저 읽는다. 명령은 각 디렉터리 안에서 실행한다.
- 에이전트(Claude Code, Codex)는 레포 루트에서 실행한다. 훅과 스킬 설정이 루트에 있다.
- 커밋은 Conventional Commits 형식, 요약은 한국어로 쓴다. 예: `feat: 로그인 폼 추가`
- `main`에서 브랜치를 따고 PR로만 머지한다. 자세한 규칙은 [git-workflow](client/docs/rules/git-workflow.md).

## 에이전트 하네스

| 경로                                         | 내용                                                       |
| -------------------------------------------- | ---------------------------------------------------------- |
| `.agents/skills/`                            | 스킬 원본. Codex가 읽고, `.claude/skills/`는 이곳의 링크다 |
| `tools/agent-hooks/`                         | 훅 스크립트 (Claude Code·Codex 공용)                       |
| `.claude/settings.json`, `.codex/hooks.json` | 도구별 훅 등록                                             |
| `lefthook.yml`                               | git hook (커밋 전 lint·format, 커밋 메시지 검사)           |
