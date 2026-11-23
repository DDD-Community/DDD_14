#!/bin/bash
# SessionStart: 새 세션이 규칙을 알고 시작하게 한다. 출력은 세션의 맥락에 들어간다.
proj=${CLAUDE_PROJECT_DIR:-.}
cd "$proj" 2>/dev/null || exit 0
echo "이 저장소의 규칙은 docs/README.md에 있다. 작업을 시작하기 전에 읽는다. 지금 단계를 계산한 결과:"
python3 scripts/status.py 2>/dev/null
exit 0
