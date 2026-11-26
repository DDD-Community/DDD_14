# 0005. 영역별 하네스 분리와 루트 공용 규칙

## 상태 (Status)

제안됨 (Proposed) — 2026-11-26. PR 리뷰에서 확정한다. [ADR 0004](0004-agent-harness.md)의 스킬·훅 위치와 팀 스킬 이름을 대체한다.

## 배경 (Context)

BE가 `server/` 안에 자체 하네스를 만들었다(PR #3). BE 하네스는 "에이전트 세션은 `server/`에서 시작한다"를 전제로 한다. 반면 FE 하네스는 레포 루트에 있었고, 내용은 FE 전용이었다. 그래서 BE 세션에 다음 문제가 생겼다.

- Claude는 실행 폴더부터 레포 루트까지의 스킬을 읽는다. 그래서 `server/`에서 시작해도 루트의 FE 스킬이 보였다.
- 루트 AGENTS.md는 모든 세션이 읽는다. 그런데 "에이전트는 레포 루트에서 실행한다"는 FE 기준 문구가 BE 설계와 충돌했다.

한편 FE는 레포 루트에서 시작해 서버 코드를 함께 참고하고 싶다. 모노레포로 합친 이유이기도 하다.

## 결정 (Decision)

| 영역           | 결정                                                                                                                                                                                                                         |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 루트           | 공용이거나 기술적으로 루트에 있어야 하는 것만 둔다: `AGENTS.md`(영역 지도와 공용 규칙), `CLAUDE.md`, 루트 세션용 훅 등록(`.claude/settings.json`, `.codex/hooks.json`), `lefthook.yml`, `.github/`, `.vscode/`, `.gitignore` |
| FE 하네스      | `client/`로 옮긴다. 스킬은 `client/.agents/skills/`(Claude용 링크는 `client/.claude/skills/`), 훅 스크립트는 `client/scripts/agent-hooks/`                                                                                   |
| 팀 스킬 이름   | `client-` 접두사를 붙인다(`client-new-feature`, `client-review-changes`, `client-verify-ui`, `client-write-adr`)                                                                                                             |
| 세션 시작 위치 | FE는 레포 루트, BE는 `server/`. 루트 AGENTS.md 맨 위에 백엔드는 `server/` 하네스만 따른다고 밝힌다                                                                                                                           |
| 규칙 적용      | 작업하는 폴더의 규칙만 따르고, 다른 폴더는 참고만 한다. 공용 규칙(브랜치·커밋, PR·이슈 템플릿, PR 병합·`main` push·force push 금지)만 함께 따른다                                                                            |
| 훅 안내        | 훅이 스킬을 요청할 때 `SKILL.md` 경로를 함께 준다. 루트에서 시작한 Codex는 `client/` 안의 스킬을 자동으로 찾지 못하기 때문이다                                                                                               |
| Codex 훅       | Codex는 BE 세션에서도 루트 `.codex/hooks.json`을 읽는다. 그래서 node가 없으면 넘어가게 하고, 훅은 `client/` 변경이 없으면 아무것도 하지 않는다                                                                               |
| git hook 등록  | pnpm 10은 의존성의 설치 스크립트를 막고, 허용해도 빌드 결과를 캐시하면 다시 실행하지 않는다. 그래서 client의 `prepare` 스크립트에서 `lefthook install`을 실행한다                                                            |

`server/`(PR #3)와 `.github/`(PR #5)는 건드리지 않는다.

고려한 대안:

- **공용 엔진 하나로 통합**: 루트 훅이 영역 설정을 읽어 FE·BE 모두를 처리한다. 하지만 BE 하네스는 bash·Python 기반의 독립된 체계라 다시 짜야 한다.
- **모두 루트에서 시작**: 한 세션에서 양쪽을 고칠 수 있다. 하지만 BE 훅의 경로와 시작 절차를 루트 기준으로 바꿔야 하고, BE가 정한 "`server/`에서 시작" 결정을 뒤집는다.
- **FE도 `client/`에서 시작**: 완전히 대칭이 된다. 하지만 서버 코드를 참고하기 불편하고, 루트에서 띄우면 FE 훅이 조용히 빠진다.
- **루트 `CLAUDE.md`를 지워 BE 세션이 루트 AGENTS.md를 읽지 않게 하기**: Claude의 특정 동작에 기대는 방식이라 이유가 드러나지 않고, Codex에는 통하지 않는다. 대신 루트 AGENTS.md를 BE가 읽어도 문제없는 내용으로만 채운다.

## 결과 (Consequences)

- BE 세션에는 FE 스킬·훅이 보이지 않는다. 루트 AGENTS.md는 BE 세션에도 읽히지만, 백엔드는 `server/` 하네스를 따르라고 안내하는 내용뿐이다.
- FE는 루트에서 시작해 서버 코드를 참고할 수 있다. `server/` 파일을 읽으면 `server/AGENTS.md`도 함께 불려오므로, 루트 AGENTS.md의 "작업하는 폴더의 규칙만 따른다"에 기댄다.
- 공용 Git 규칙(`client/docs/rules/git-workflow.md`)은 BE 문서가 이 경로를 참조하고 있어서 그대로 둔다. 루트로 옮기는 일과 공용 PR·이슈 스킬은 BE와 함께 정한다.
