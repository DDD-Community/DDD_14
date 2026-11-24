# 0003. Client 테스트 도구

## 상태 (Status)

제안됨 (Proposed) — 2026-11-22. PR 리뷰에서 확정한다.

## 배경 (Context)

AI 코딩 에이전트가 작업 결과를 스스로 확인할 수 있는 pass/fail 수단이 필요했다. 또한 BE(`server/`)와 병행 개발하므로 API가 완성되기 전에도 네트워크를 포함한 동작을 테스트할 수 있어야 했다.

## 결정 (Decision)

- 테스트 러너: **Vitest**. Vite 설정(별칭, 플러그인)을 그대로 쓴다.
- 컴포넌트 테스트: **React Testing Library** + `@testing-library/user-event` + `@testing-library/jest-dom`, 환경은 **jsdom**. `@testing-library/dom`은 RTL이 요구하는 peer 의존성이라 함께 설치한다.
- API 모킹: **MSW**. 핸들러가 없는 요청은 실패시켜 실제 네트워크로 새는 테스트를 막는다.
- E2E(Playwright test)는 핵심 플로우가 생기는 Phase 3에서 도입한다.

버전은 공급망 안전을 위해 배포된 지 7일이 지난 버전으로 골랐다.

고려한 대안:

- **Jest**: 생태계가 넓지만 Vite 설정과 별도로 변환 설정을 맞춰야 한다.
- **happy-dom**: jsdom보다 빠르지만 호환성 이슈 사례가 더 많아 jsdom을 택했다.
- **axios 모킹(vi.mock)**: 간단하지만 요청 형태를 검증하지 못하고, dev 서버와 핸들러를 공유할 수 없다.

## 결과 (Consequences)

- `pnpm test`로 에이전트와 사람이 같은 방식으로 검증한다. `pnpm verify`와 CI에도 포함된다.
- jsdom의 XHR은 cross-origin 요청에 CORS 검사를 적용한다. 테스트용 API 주소(`.env.test`)를 jsdom 기본 origin과 같게 둬서 피한다.
- 브라우저 dev 서버용 MSW worker는 첫 API 작업에서 추가한다.
