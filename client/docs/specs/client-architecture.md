# Client 아키텍처

결정 배경은 [ADR 0002](../adr/0002-client-folder-structure.md) 참고.

## 폴더 구조

```text
src/
├─ main.tsx      진입점 (레이어 밖)
├─ index.css     Tailwind 진입 CSS
├─ app/          전역 Provider, 라우터
├─ pages/        라우트 단위 화면. features를 조립한다
│  └─ <name>/    <Name>Page.tsx + 이 페이지에서만 쓰는 하위 컴포넌트
├─ features/     기능 단위 UI·훅·API·상태
│  └─ <name>/    components/ hooks/ api/ model/ index.ts
├─ shared/       도메인과 무관한 공용 코드
│  ├─ lib/       api, cn, query-client 등
│  └─ ui/        공용 UI 컴포넌트
└─ test/         테스트 공용 설정 (레이어 밖)
```

## 레이어와 의존 방향

의존 방향은 `app → pages → features → shared`이다. 같은 레이어나 아래 레이어만 import할 수 있다. 단, feature끼리는 import하지 않는다.

| 레이어     | 책임                              | import할 수 있는 레이어                    |
| ---------- | --------------------------------- | ------------------------------------------ |
| `app`      | 진입, 전역 Provider, 라우터       | app, pages, features, shared               |
| `pages`    | 라우트 단위 화면. features를 조립 | pages, features, shared                    |
| `features` | 기능 단위 UI, 훅, API 호출, 상태  | 자기 feature, shared (다른 feature는 금지) |
| `shared`   | 도메인과 무관한 공용 코드         | shared                                     |

## feature 규칙

- 밖에서는 `@/features/<name>`(`index.ts`)으로 공개된 것만 import한다.
- feature 안에서는 자기 내부 파일을 `@/features/<name>/...`로 import해도 된다.
- 두 feature가 함께 쓰는 코드는 `shared/`로 옮긴다. 두 feature를 함께 보여 주는 화면은 `pages/`에서 조립한다.
- 서버 상태는 TanStack Query(`api/`), 클라이언트 상태는 zustand(`model/`)에 둔다. 서버 데이터를 zustand에 복사하지 않는다.

## 강제 방식

| 규칙                                                           | 검사                                             |
| -------------------------------------------------------------- | ------------------------------------------------ |
| 레이어 역방향 import 금지 (`export ... from`, `import()` 포함) | `ttadak/architecture` (`lint-plugins/ttadak.js`) |
| feature 간 import 금지                                         | `ttadak/architecture`                            |
| 다른 feature 내부 파일 import 금지                             | `ttadak/architecture`                            |
| 상위 상대경로(`../`) import 금지                               | `no-restricted-imports`                          |
| 순환 의존 금지                                                 | `import/no-cycle`                                |

## 변경 이력

- 2026-11-22: 최초 작성. `src/lib/*`를 `src/shared/lib/*`로 옮겼다. ([ADR 0002](../adr/0002-client-folder-structure.md))
