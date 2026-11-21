# 0001. Client 빌드·린트·포맷 도구 선택

## 상태 (Status)

수락됨 (Accepted) — 2026-11-21

## 배경 (Context)

`client/`를 React + TypeScript로 새로 시작하면서 패키지 매니저, 빌드, 린트, 포맷 도구를 정해야 했다.

## 결정 (Decision)

- 패키지 매니저: pnpm.
- 빌드: 최신 `create-vite` `react-ts` 템플릿 기본값(Vite + TypeScript 7)을 그대로 쓴다.
- Lint: 템플릿 기본값 oxlint를 쓴다.
- Format: Prettier를 추가해 단독 실행한다.

고려한 대안:

- **npm**: 별도 설치가 필요 없지만 설치 속도·디스크 사용량·엄격한 의존성 해석에서 pnpm을 택했다.
- **ESLint(flat config + typescript-eslint)**: 규칙·플러그인 생태계가 넓지만, typescript-eslint 8.x가 TypeScript `<6.1`만 지원해 TypeScript를 6으로 낮춰야 한다. 템플릿 기본값을 따르는 쪽을 택했다.

## 결과 (Consequences)

- 템플릿 업그레이드를 따라가기 쉽고, TypeScript 7과 oxlint로 타입 체크·lint가 빠르다.
- ESLint 전용 플러그인은 쓸 수 없다. 필요해지면 이 ADR을 Superseded로 바꾸고 새 ADR로 다시 검토한다.
