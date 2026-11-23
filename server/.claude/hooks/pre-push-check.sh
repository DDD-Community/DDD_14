#!/bin/bash
# PreToolUse(Bash): git push 전에 현재 커밋을 scripts/check.sh로 검증했는지 확인한다.
# check.sh가 통과하면 커밋 해시를 기록한다. 기록이 현재 커밋과 다르면 막는다.
input=$(cat)
tool=$(jq -r '.tool_name // empty' <<<"$input" 2>/dev/null)
[ "$tool" = "Bash" ] || exit 0
cmd=$(jq -r '.tool_input.command // empty' <<<"$input" 2>/dev/null)
cwd=$(jq -r '.cwd // empty' <<<"$input" 2>/dev/null)
proj=${CLAUDE_PROJECT_DIR:-${cwd:-.}}
grep -Eq '(^|[;&|[:space:]])git push( |$)' <<<"$cmd" || exit 0
rec=$(git -C "$proj" rev-parse --git-path check-passed 2>/dev/null)
head=$(git -C "$proj" rev-parse HEAD 2>/dev/null)
[ -z "$head" ] && exit 0
[[ "$rec" = /* ]] || rec="$proj/$rec"
if [ ! -f "$rec" ] || [ "$(cat "$rec")" != "$head" ]; then
  echo "차단: 현재 커밋(${head:0:7})을 scripts/check.sh로 검증하지 않았다. check.sh를 통과시킨 뒤 push한다." >&2
  exit 2
fi
exit 0
