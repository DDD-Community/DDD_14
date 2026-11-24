# Client 개발 환경

결정 배경은 [ADR 0001](../adr/0001-client-tooling.md), [ADR 0003](../adr/0003-client-test-stack.md), [ADR 0004](../adr/0004-agent-harness.md) 참고. 폴더 구조와 의존 방향은 [client-architecture](client-architecture.md)에 있다.

## 구성

| 항목           | 도구                                                                                                                 | 설정 파일                                  |
| -------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| 런타임         | Node `>=22.12.0` (Vite 8 요구 사항)                                                                                  | `package.json`의 `engines`                 |
| 패키지 매니저  | pnpm `10.28.0` (고정)                                                                                                | `package.json`의 `packageManager`, `pnpm-lock.yaml` |
| 빌드/개발 서버 | Vite + `@vitejs/plugin-react`, `@tailwindcss/vite`                                                                   | `vite.config.ts`                           |
| 언어           | TypeScript `~7.0`                                                                                                    | `tsconfig*.json`                           |
| Lint           | oxlint (`react`, `typescript`, `oxc`, `import`, `vitest` 플러그인) + 타입 인식 규칙(`oxlint-tsgolint`) + 커스텀 규칙 | `.oxlintrc.json`, `lint-plugins/ttadak.js` |
| Format         | Prettier (세미콜론, 작은따옴표, trailingComma all, printWidth 100)                                                   | `.prettierrc.json`, `.prettierignore`      |
| 테스트         | Vitest + jsdom + React Testing Library + MSW                                                                         | `vite.config.ts`의 `test`, `src/test/`     |
| git hook       | lefthook (pre-commit: Prettier·oxlint, commit-msg: 형식 검사)                                                        | 루트 `lefthook.yml`                        |
| 브라우저 확인  | `@playwright/cli`                                                                                                    | —                                          |

## 주요 라이브러리

| 용도            | 라이브러리                | 비고                                           |
| --------------- | ------------------------- | ---------------------------------------------- |
| 스타일          | Tailwind CSS v4           | `src/index.css`의 `@import 'tailwindcss'`      |
| className 결합  | `clsx` + `tailwind-merge` | `@/shared/lib/cn`의 `cn()`으로만 사용          |
| HTTP            | axios                     | `@/shared/lib/api`의 `api` 인스턴스로만 요청   |
| 서버 상태       | TanStack Query v5         | `@/shared/lib/query-client`, devtools는 개발용 |
| 클라이언트 상태 | zustand                   | UI·세션 상태만. 서버 데이터는 복사 금지        |
| 날짜            | date-fns                  | 한국어는 `date-fns/locale`의 `ko`              |

`cn()`, `api` 규칙은 lint(`no-restricted-imports`)가 강제한다. 타입만 가져오는 import(`import type { AxiosError } from 'axios'`)는 허용한다.

기다리지 않을 Promise(예: `queryClient.invalidateQueries()`)는 `void`를 붙여 의도를 드러낸다. lint(`no-floating-promises`)가 표시 없는 Promise를 잡는다.

## 테스트

| 용도     | 라이브러리                                              | 비고                                                          |
| -------- | ------------------------------------------------------- | ------------------------------------------------------------- |
| 러너     | Vitest                                                  | globals를 쓰지 않는다. `vitest`에서 import                    |
| 컴포넌트 | `@testing-library/react`, `@testing-library/user-event` | 환경은 jsdom                                                  |
| matcher  | `@testing-library/jest-dom`                             | `src/test/setup.ts`에서 등록                                  |
| API 모킹 | MSW                                                     | 기본 핸들러 `src/test/handlers.ts`, 서버 `src/test/server.ts` |

작성 규칙은 [testing](../rules/testing.md)에 있다.

## 경로 별칭

`@/` → `src/`. `tsconfig.app.json`의 `paths`와 `vite.config.ts`의 `resolve.alias` 두 곳에 같이 정의한다.

## 환경 변수

### 환경

| 환경  | Vite mode     | 파일               | 명령         |
| ----- | ------------- | ------------------ | ------------ |
| local | `development` | `.env.development` | `pnpm dev`   |
| test  | `test`        | `.env.test`        | `pnpm test`  |
| prod  | `production`  | `.env.production`  | `pnpm build` |

- `.env`는 모든 환경 공통값, `.env.local`·`.env.[mode].local`은 개인 덮어쓰기(git 무시)다.
- local의 mode 이름이 `local`이 아닌 이유: `.env.local`은 Vite가 모든 mode에 적용하는 개인 덮어쓰기 파일로 예약해 두었다.
- 코드에서 환경 분기는 `import.meta.env.VITE_APP_ENV`로 한다. `import.meta.env.MODE`나 `PROD`는 쓰지 않는다(나중에 dev 환경을 `vite build --mode dev`로 추가하면 `PROD`가 `true`라 prod와 구분되지 않는다). lint(`ttadak/no-env-mode`)가 강제한다.
- test 환경의 `VITE_API_BASE_URL`은 jsdom 기본 origin(`http://localhost:3000`)과 같게 둔다. jsdom의 XHR이 cross-origin 요청에 CORS 검사를 적용하기 때문이다.

### 규칙

- 모든 `.env*` 파일은 커밋된다(`*.local` 제외). 비밀 값은 넣지 않는다.
- 클라이언트에 노출할 변수는 `VITE_` 접두사를 붙인다.
- 새 변수를 추가하면 `src/vite-env.d.ts`의 `ImportMetaEnv`에 타입을, 아래 표에 설명을 함께 추가한다. `pnpm docs:check`가 세 곳이 일치하는지 검사한다.

### 변수

| 변수                | 설명                |
| ------------------- | ------------------- |
| `VITE_APP_ENV`      | `'local' \| 'prod'` |
| `VITE_API_BASE_URL` | API 서버 base URL   |

## 스크립트

| 명령                                | 동작                                                          |
| ----------------------------------- | ------------------------------------------------------------- |
| `pnpm dev`                          | 개발 서버 (local)                                             |
| `pnpm build`                        | prod 빌드                                                     |
| `pnpm preview`                      | 빌드 결과 미리보기                                            |
| `pnpm typecheck`                    | 타입 체크 (`tsc -b`)                                          |
| `pnpm lint` / `pnpm lint:fix`       | oxlint 검사(경고도 실패) / 자동 수정                          |
| `pnpm format` / `pnpm format:check` | Prettier 적용 / 검사                                          |
| `pnpm test` / `pnpm test:watch`     | 테스트 1회 실행 / watch 모드                                  |
| `pnpm verify:fast`                  | typecheck + lint                                              |
| `pnpm verify`                       | typecheck → lint → format:check → test → build (완료 전 필수) |
| `pnpm docs:check`                   | 문서 링크·ADR 번호·plan 파일명·환경 변수 정합성 검사          |

## 변경 이력

- 2026-11-24: pnpm을 `10.28.0`으로 고정하고 Node 런타임 요구 사항(`>=22.12.0`)을 명시.
- 2026-11-22: 경로를 `@/lib/*` → `@/shared/lib/*`로 변경 ([ADR 0002](../adr/0002-client-folder-structure.md)). 테스트 도구·test 환경 추가 ([ADR 0003](../adr/0003-client-test-stack.md)). 타입 인식 lint·커스텀 규칙·lefthook·스크립트 추가 ([ADR 0004](../adr/0004-agent-harness.md)).
