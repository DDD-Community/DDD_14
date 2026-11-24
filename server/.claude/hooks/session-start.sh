#!/bin/bash
# SessionStart: 새 세션이 규칙을 알고 시작하게 한다. 출력은 세션의 맥락에 들어간다.
proj=${CLAUDE_PROJECT_DIR:-.}
cd "$proj" 2>/dev/null || exit 0
# 다른 훅은 jq로 입력을 읽고, 읽지 못하면 통과시킨다. jq가 없으면 가드가 말없이 꺼지므로 먼저 알린다.
if ! command -v jq >/dev/null 2>&1; then
  echo "경고: jq가 없어 훅이 모두 꺼져 있다(편집 가드, 일지 검사, push 검사, 에이전트 제한이 걸리지 않는다). 사용자에게 알리고 설치하게 한다: macOS는 brew install jq, Ubuntu는 sudo apt install jq."
fi
echo "이 저장소의 규칙은 docs/README.md에 있다. 작업을 시작하기 전에 읽는다. 지금 단계를 계산한 결과:"
python3 scripts/status.py 2>/dev/null
exit 0
