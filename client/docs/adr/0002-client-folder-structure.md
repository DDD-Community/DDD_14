# 0002. Client 폴더 구조와 의존 방향

## 상태 (Status)

제안됨 (Proposed) — 2026-11-22. PR 리뷰에서 확정한다.

## 배경 (Context)

기능 코드가 생기기 전에 폴더 구조와 의존 방향을 정해야 했다. 두 사람이 AI 코딩 에이전트와 함께 개발하므로, 에이전트가 어디에 무엇을 둘지 매번 추측하지 않도록 구조를 명확히 하고 기계적으로 강제할 필요가 있었다. 에이전트는 레포에 이미 있는 패턴을 그대로 따라 하기 때문에, 코드가 0줄인 지금 정하는 비용이 가장 작다.

## 결정 (Decision)

`app → pages → features → shared` 4개 레이어를 두고, 위 레이어만 아래 레이어를 import할 수 있게 한다. feature끼리는 import하지 않고, feature 밖에서는 `index.ts`로 공개된 것만 쓴다. 구조와 규칙은 [client-architecture spec](../specs/client-architecture.md)에 정의하고, oxlint 커스텀 규칙(`ttadak/architecture`)으로 강제한다. 기존 `src/lib/*`는 `src/shared/lib/*`로 옮긴다.

고려한 대안:

- **Feature-Sliced Design(FSD) 전체**: entities, widgets 등 레이어가 더 세분화되어 있고 전용 linter(Steiger)도 있다. 하지만 2인이 짧은 기간에 진행하는 프로젝트에는 레이어 판단 비용이 크다고 봤다. 필요해지면 이 구조에서 확장할 수 있다.
- **구조만 정하고 문서로 안내**: 에이전트가 문서를 놓치면 그대로 어긋난다. 규칙 위반을 lint 오류(고치는 방법 포함)로 바로 돌려주는 쪽을 택했다.
- **dependency-cruiser로 경계 검사**: 표현력이 좋지만 도구가 하나 더 늘어난다. ADR 0001에서 고른 oxlint의 JS 플러그인으로 충분했다.

## 결과 (Consequences)

- 에이전트와 사람이 같은 기준으로 코드 위치를 정하고, 위반은 lint 단계에서 바로 드러난다.
- oxlint JS 플러그인은 아직 알파(2026-03 발표)다. 문제가 생기면 같은 규칙을 dependency-cruiser로 옮긴다.
- 두 feature에 걸친 코드는 `shared/` 승격이나 `pages/` 조립이 필요해서 약간의 이동 비용이 생긴다.
