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
| HTTP            | axios                     |                                           |
| 클라이언트 상태 | zustand                   |                                           |
| 날짜            | date-fns                  | 한국어는 `date-fns/locale`의 `ko`         |

## 경로 별칭

`@/` → `src/`. `tsconfig.app.json`의 `paths`와 `vite.config.ts`의 `resolve.alias` 두 곳에 같이 정의한다.

## 환경 변수

| 파일         | 용도                      | git  |
| ------------ | ------------------------- | ---- |
| `.env`       | 공통 기본값. 비밀 값 금지 | 커밋 |
| `.env.local` | 개인 로컬 덮어쓰기        | 무시 |

- 클라이언트에 노출할 변수는 `VITE_` 접두사를 붙인다.
- 새 변수를 추가하면 `src/vite-env.d.ts`의 `ImportMetaEnv`에 타입을 함께 추가한다.

| 변수                | 설명              |
| ------------------- | ----------------- |
| `VITE_API_BASE_URL` | API 서버 base URL |

## 스크립트

| 명령                                | 동작                    |
| ----------------------------------- | ----------------------- |
| `pnpm dev`                          | 개발 서버               |
| `pnpm build`                        | `tsc -b && vite build`  |
| `pnpm preview`                      | 빌드 결과 미리보기      |
| `pnpm lint` / `pnpm lint:fix`       | oxlint 검사 / 자동 수정 |
| `pnpm format` / `pnpm format:check` | Prettier 적용 / 검사    |
