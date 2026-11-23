#!/usr/bin/env bash
# 슬라이스를 검증한다(ADR-0001의 6단계). 하나라도 실패하면 0이 아닌 값으로 끝난다.
#   1. docs-lint: 문서 규칙
#   2. trace: spec의 AC와 domain의 R이 테스트에 닿는지
#   3. 빌드와 테스트: ./gradlew check (Spotless 형식 검사와 ArchUnit 포함한 테스트). 빌드 파일이 아직 없으면 건너뛰고 표시한다.
# 통과하면 현재 커밋 해시를 기록한다. push 전에 그 기록을 확인할 수 있다.
set -uo pipefail
# 모노레포에서 server/가 프로젝트 폴더다. git 저장소의 맨 위가 아니라 이 스크립트의 위 폴더로 간다.
cd "$(cd "$(dirname "$0")/.." && pwd)"

fail=0

echo "[check] 1/4 docs-lint"
if ! python3 scripts/docs_lint.py --all; then fail=1; fi

echo "[check] 2/4 trace"
if ! python3 scripts/trace_check.py; then fail=1; fi

echo "[check] 3/4 scripts 테스트"
if ! python3 -m unittest discover -s scripts -p 'test_*.py' >/dev/null 2>&1; then echo "[check] scripts 테스트 실패. python3 -m unittest discover -s scripts -p 'test_*.py'로 확인한다" >&2; fail=1; fi

echo "[check] 4/4 build and test"
if [ -x ./gradlew ]; then
  if ! ./gradlew check "$@"; then fail=1; fi
else
  echo "[check] ./gradlew가 없어 빌드와 테스트를 건너뛴다(코드가 아직 없다)"
fi

if [ "$fail" -ne 0 ]; then
  echo "[check] 실패" >&2
  exit 1
fi

if git rev-parse HEAD >/dev/null 2>&1 && [ -z "$(git status --porcelain --untracked-files=no -- .)" ]; then
  git rev-parse HEAD > "$(git rev-parse --git-path check-passed)"
  echo "[check] 통과 기록: $(git rev-parse --short HEAD)"
else
  echo "[check] 통과. 커밋하지 않은 변경이 있거나 커밋이 없어 통과 기록은 남기지 않는다"
fi
