# Client 개발 환경

결정 배경은 [ADR 0001](../adr/0001-client-tooling.md) 참고.

## 구성

| 항목           | 도구                                                               | 설정 파일                             |
| -------------- | ------------------------------------------------------------------ | ------------------------------------- |
| 패키지 매니저  | pnpm                                                               | `pnpm-lock.yaml`                      |
| 빌드/개발 서버 | Vite + `@vitejs/plugin-react`, `@tailwindcss/vite`                 | `vite.config.ts`                      |
| 언어           | TypeScript `~7.0`                                                  | `tsconfig*.json`                      |
| Lint           | oxlint (`react`, `typescript`, `oxc` 플러그인)                     | `.oxlintrc.json`                      |
| Format         | Prettier (세미콜론, 작은따옴표, trailingComma all, printWidth 100) | `.prettierrc.json`, `.prettierignore` |

## 주요 라이브러리

| 용도            | 라이브러리                | 비고                                      |
| --------------- | ------------------------- | ----------------------------------------- |
| 스타일          | Tailwind CSS v4           | `src/index.css`의 `@import 'tailwindcss'` |
| className 결합  | `clsx` + `tailwind-merge` | `@/lib/cn`의 `cn()`으로만 사용            |
| HTTP            | axios                     | `@/lib/api`의 `api` 인스턴스로만 요청     |
| 서버 상태       | TanStack Query v5         | `@/lib/query-client`, devtools는 개발용   |
| 클라이언트 상태 | zustand                   | UI·세션 상태만. 서버 데이터는 복사 금지   |
| 날짜            | date-fns                  | 한국어는 `date-fns/locale`의 `ko`         |

## 경로 별칭

`@/` → `src/`. `tsconfig.app.json`의 `paths`와 `vite.config.ts`의 `resolve.alias` 두 곳에 같이 정의한다.

## 환경 변수

### 환경

| 환경  | Vite mode     | 파일               | 명령         |
| ----- | ------------- | ------------------ | ------------ |
| local | `development` | `.env.development` | `pnpm dev`   |
| prod  | `production`  | `.env.production`  | `pnpm build` |

- `.env`는 모든 환경 공통값, `.env.local`·`.env.[mode].local`은 개인 덮어쓰기(git 무시)다.
- local의 mode 이름이 `local`이 아닌 이유: `.env.local`은 Vite가 모든 mode에 적용하는 개인 덮어쓰기 파일로 예약해 두었다.
- 코드에서 환경 분기는 `import.meta.env.VITE_APP_ENV`로 한다. `import.meta.env.MODE`나 `PROD`는 쓰지 않는다(나중에 dev 환경을 `vite build --mode dev`로 추가하면 `PROD`가 `true`라 prod와 구분되지 않는다).

### 규칙

- 모든 `.env*` 파일은 커밋된다(`*.local` 제외). 비밀 값은 넣지 않는다.
- 클라이언트에 노출할 변수는 `VITE_` 접두사를 붙인다.
- 새 변수를 추가하면 `src/vite-env.d.ts`의 `ImportMetaEnv`에 타입을 함께 추가한다.

### 변수

| 변수                | 설명                |
| ------------------- | ------------------- |
| `VITE_APP_ENV`      | `'local' \| 'prod'` |
| `VITE_API_BASE_URL` | API 서버 base URL   |

## 스크립트

| 명령                                | 동작                    |
| ----------------------------------- | ----------------------- |
| `pnpm dev`                          | 개발 서버 (local)       |
| `pnpm build`                        | prod 빌드               |
| `pnpm preview`                      | 빌드 결과 미리보기      |
| `pnpm lint` / `pnpm lint:fix`       | oxlint 검사 / 자동 수정 |
| `pnpm format` / `pnpm format:check` | Prettier 적용 / 검사    |
