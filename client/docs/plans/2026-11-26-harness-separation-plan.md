# FE 하네스를 client/로 분리하고 루트는 공용만 남기기

- 상태: 완료
- 관련: [ADR 0004](../adr/0004-agent-harness.md), BE 하네스 PR #3, 템플릿 PR #5

## 목표

- BE가 `server/`에서 시작하는 자체 하네스(PR #3)를 쓰므로, 루트의 FE 하네스가 BE 세션에 영향을 주지 않게 한다.
- 루트에는 공용이거나 기술적으로 루트에 있어야 하는 것만 남긴다.
- FE는 지금처럼 레포 루트에서 시작해 서버 코드를 참고할 수 있게 한다.

## 범위 밖

- `server/` 전체 (PR #3), `.github/` (PR #5)
- `client/docs/rules/git-workflow.md`의 위치 (BE 문서가 공용 규칙으로 참조)
- 공용 PR·이슈 스킬 (BE 절차를 바꿔야 해서 BE와 같이 정한다)

## 단계

- [x] 1. FE 스킬(팀 스킬은 `client-` 접두사), 외부 스킬, `skills-lock.json`을 `client/`로 이동
- [x] 2. 훅 스크립트를 `client/scripts/agent-hooks/`로 이동, 루트 등록 파일은 경로만 갱신
- [x] 3. 훅이 스킬을 요청할 때 SKILL.md 경로를 함께 안내
- [x] 4. `.codex/hooks.json`에 node가 없으면 넘어가는 보호 추가, `.vscode` 포맷 설정을 client 파일로 한정
- [x] 5. pnpm 10에서도 git hook이 등록되게 함 (`prepare`에서 `lefthook install`)
- [x] 6. 루트 AGENTS.md를 FE·BE 지도와 공용 규칙으로 다시 씀
- [x] 7. client 문서·스킬 이름 갱신, ADR 0005 작성, ADR 0004에 일부 대체 표시

## 검증 방법

- `pnpm verify`, `pnpm docs:check`
- 루트에 스킬 폴더가 남지 않았는지 확인
- 훅 시나리오: 서버만 바뀜 → 통과, client 변경 → 새 스킬 이름·경로로 요청, node 없음 → Codex 훅 통과
- 새로 설치했을 때 lefthook 자동 등록

## 진행 로그

- 2026-11-26: 계획 합의, 작업 시작
- 2026-11-26: 1~7단계 완료. 검증 중 stop-gate가 심볼릭 링크를 읽다 멈추는 문제, 외부 스킬이 Prettier 검사에 걸리는 문제, pnpm 캐시 때문에 lefthook이 등록되지 않는 문제를 찾아 함께 고쳤다. 리뷰가 끝나면 수명주기 규칙대로 이 plan을 삭제한다.
