# Client 개발 환경

결정 배경은 [ADR 0001](../adr/0001-client-tooling.md) 참고.

## 구성

| 항목           | 도구                                                                    | 설정 파일                             |
| -------------- | ----------------------------------------------------------------------- | ------------------------------------- |
| 패키지 매니저  | pnpm                                                                    | `pnpm-lock.yaml`                      |
| 빌드/개발 서버 | Vite + `@vitejs/plugin-react`                                           | `vite.config.ts`                      |
| 언어           | TypeScript `~7.0`                                                       | `tsconfig*.json`                      |
| Lint           | oxlint (`react`, `typescript`, `oxc` 플러그인)                          | `.oxlintrc.json`                      |
| Format         | Prettier (세미콜론 없음, 작은따옴표, trailingComma all, printWidth 100) | `.prettierrc.json`, `.prettierignore` |

## 스크립트

| 명령                                | 동작                    |
| ----------------------------------- | ----------------------- |
| `pnpm dev`                          | 개발 서버               |
| `pnpm build`                        | `tsc -b && vite build`  |
| `pnpm preview`                      | 빌드 결과 미리보기      |
| `pnpm lint` / `pnpm lint:fix`       | oxlint 검사 / 자동 수정 |
| `pnpm format` / `pnpm format:check` | Prettier 적용 / 검사    |
