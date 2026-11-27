#!/bin/bash
# PostToolUse(Edit|Write|MultiEdit): docs/ 아래의 문서와 AGENTS.md를 쓴 직후 docs/README.md의 기계 검사를 돌린다.
# 위반이 있으면 종료 코드 2로 알린다(쓴 직후 고치게 하려는 것이다).
input=$(cat)
file=$(jq -r '.tool_input.file_path // empty' <<<"$input" 2>/dev/null)
cwd=$(jq -r '.cwd // empty' <<<"$input" 2>/dev/null)
[ -z "$file" ] && exit 0
proj=${CLAUDE_PROJECT_DIR:-${cwd:-.}}
rel=${file#"$proj"/}
case "$rel" in
  docs/*.md|docs/*/*.md|AGENTS.md) ;;
  *) exit 0 ;;
esac
out=$(python3 "$proj/scripts/docs_lint.py" "$proj/$rel" 2>&1)
status=$?
if [ $status -ne 0 ]; then
  echo "docs-lint: $rel의 위반을 고친다." >&2
  echo "$out" >&2
  exit 2
fi
exit 0
