# verify — 검증

기계가 먼저 확인하고, 독립 리뷰어(`code-reviewer`)가 코드를 점검한다. 하나라도 실패하면 `implement`로 돌아간다. 검증을 건너뛰고 종료할 수 없다(ADR-0001의 2번).

## 읽는 것

- `./scripts/check.sh`의 출력.
- 변경(`git diff <base>...HEAD`)과 닿는 문서의 해당 줄.

## 절차

1. `./scripts/check.sh`를 실행한다. 이유: 도구가 최종 판정이다. 빌드와 테스트, `docs-lint`, ID 추적(`trace_check.py`)이 한 번에 돈다. 실패하면 2로 가지 않고 `implement`로 돌아간다.
2. `git diff <base>...HEAD`를 `_workspace/diff-NN.patch`에 저장한다.
3. `code-reviewer`를 부른다. `review` 스킬의 code 절차를 따른다. 입력은 diff 경로와 plan 경로뿐이다. 이유: 성능, 코드 품질, 보안의 판단은 코드를 쓴 세션이 못 본다. conformance(정책과 코드의 대조)는 `close`에서 한 번 한다.
4. 리포트를 `shared/리뷰-결과-합치기.md`로 합치고 `docs/review/`에 기록한다. 리포트 전문을 사용자에게 보인다.
5. 판정으로 분기한다.

| 판정 | 행동 |
|---|---|
| `PASS` | 6으로 간다 |
| `PASS_WITH_FIXES` | 권고를 보이고 반영 여부를 사용자에게 묻는다. 반영하면 `implement`로 돌아가 고치고 `check.sh`부터 다시 한다 |
| `FAIL` | 차단 항목이 코드 문제면 `implement`로 돌아간다. ADR이 틀렸을 수 있으면 사용자에게 올린다(ADR을 스스로 고치지 않는다) |

6. 통과하면 plan의 작업을 `완료`로 바꾼다. 사용자가 원하면 `explain-diff` 스킬로 변경을 해설한다. 원하지 않으면 종료로 간다. 스텝이 끝나면 일지를 쓴다.

## 하지 않는 일

- 기준을 낮춰 통과시키지 않는다. 재시도의 한도는 `work`의 "공통 규칙"이다.
- `code-reviewer`의 PASS로 `check.sh`의 실패를 덮지 않는다.
