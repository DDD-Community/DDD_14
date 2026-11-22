# Testing Rule

테스트를 작성하거나 고칠 때 따르는 규칙이다. 도구 구성은 [client-tooling](../specs/client-tooling.md#테스트)에 있다.

## 무엇을 어떻게 테스트하나

| 대상                      | 방법                                                  | 기준                                  |
| ------------------------- | ----------------------------------------------------- | ------------------------------------- |
| 훅·유틸·상태 로직·폼 검증 | Vitest                                                | 필수. **실패하는 테스트를 먼저** 쓴다 |
| 컴포넌트                  | React Testing Library                                 | 핵심 동작만, 사용자 행동 단위         |
| API 연동                  | MSW                                                   | 실제 네트워크 요청 금지               |
| 화면·시각 디테일          | 브라우저 확인 ([ui-verification](ui-verification.md)) | 테스트 대신 직접 확인                 |

## 작성 규칙

- 테스트 파일은 대상 옆에 `<name>.test.ts(x)`로 둔다.
- 테스트 이름은 "무엇을 한다" 형태의 한국어로 쓴다. 예: `it('충돌하는 Tailwind 클래스는 뒤쪽 값을 남긴다')`
- `describe`, `it`, `expect`는 `vitest`에서 import한다. globals를 쓰지 않는다.
- 요소는 `getByRole` → `getByLabelText` → `getByText` 순서로 찾는다. test id는 마지막 수단이다.
- 사용자 입력은 `@testing-library/user-event`로 흉내 낸다.
- API 응답은 MSW로 만든다. 모든 테스트에 쓰는 핸들러는 `src/test/handlers.ts`, 테스트마다 다른 응답은 테스트 안에서 `server.use(...)`로 덮어쓴다.
- 핸들러가 없는 요청은 실패한다(`onUnhandledFrame: 'error'`). 실패하면 핸들러를 추가한다.

## 금지

- 테스트를 지우거나 `.skip`·`.only`로 통과시키지 않는다. `.skip`·`.only`는 lint가 막는다.
- 기대값을 구현에 맞춰 약하게 바꾸지 않는다. 테스트가 틀렸다고 판단되면 멈추고 사람에게 묻는다.

## 명령

| 명령               | 용도             |
| ------------------ | ---------------- |
| `pnpm test`        | 전체 1회 실행    |
| `pnpm test <파일>` | 특정 파일만 실행 |
| `pnpm test:watch`  | watch 모드       |
