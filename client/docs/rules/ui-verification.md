# UI Verification Rule

화면 파일(`.tsx`, `.css`)을 바꾸면 브라우저에서 직접 확인한다. 타입 체크와 테스트는 화면이 실제로 맞게 보이는지 보장하지 않는다.

## 절차 (`client-verify-ui` 스킬)

1. `client/`에서 `pnpm dev`를 띄운다 (http://localhost:5173). 이미 떠 있으면 그대로 쓴다.
2. `pnpm exec playwright-cli`로 바뀐 화면을 연다. 사용자처럼 클릭하고 입력해서 바뀐 동작을 확인한다.
3. `playwright-cli console`로 콘솔 에러가 없는지 확인한다.
4. `playwright-cli screenshot`으로 스크린샷을 `client/.screenshots/`(git 무시)에 남기고, PR에 첨부한다.

처음 한 번은 브라우저 설치가 필요하다: `pnpm exec playwright-cli install-browser`

## 확인 항목

- 디자인 시안과 일치한다 (간격, 색, 글꼴)
- 로딩·에러·빈 상태가 보인다
- 좁은 화면(모바일 폭)에서 깨지지 않는다
- 키보드로 조작할 수 있고 포커스가 보인다
