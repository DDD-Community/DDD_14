#!/bin/bash
# PreToolUse(Edit|Write|MultiEdit): 편집 가드(ADR-0001의 4번과 훅 표).
#   - src/main을 고치는데 승인된 plan이 없으면 막지 않고 알린다(통과). 이유: 슬라이스 밖의 수정(병합 뒤의 수정)은 승인할 plan이 없다.
#     슬라이스 안에서 plan 없이 구현하는 것은 work 스킬의 plan 단계가 1차로 막는다. 브랜치 전략이 정해지면 fix 브랜치만 예외로 두는 쪽으로 올린다.
#   - docs/spec은 승인된 plan이 있는 동안(구현 중) 승인된 spec을 고치지 않는다. 이유: 코드에 맞춰 spec을 고치면 문서가 기준이 아니게 된다.
#   - .env 파일은 쓰지 않는다.
# 막는 경우가 아니면 통과시킨다. 입력을 읽지 못해도 통과시킨다(작업을 멈추는 쪽의 오류가 더 크다).
input=$(cat)
file=$(jq -r '.tool_input.file_path // empty' <<<"$input" 2>/dev/null)
cwd=$(jq -r '.cwd // empty' <<<"$input" 2>/dev/null)
[ -z "$file" ] && exit 0
proj=${CLAUDE_PROJECT_DIR:-${cwd:-.}}
rel=${file#"$proj"/}

status_of() { grep -m1 '^- 상태:' "$1" 2>/dev/null | sed 's/^- 상태:[[:space:]]*//'; }
approved_plan_exists() {
  local f s
  for f in "$proj"/docs/plan/*.md; do
    [ -f "$f" ] || continue
    s=$(status_of "$f")
    case "$s" in 승인*) return 0 ;; esac
  done
  return 1
}

case "$rel" in
  .env|.env.*)
    case "$rel" in .env.example) exit 0 ;; esac
    echo "차단: .env 파일은 쓰지 않는다($rel). 비밀 값은 환경 변수로 둔다." >&2
    exit 2 ;;
  src/main/*)
    if ! approved_plan_exists; then
      printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"승인된 plan이 없다. 새 기능의 구현이면 멈추고 work의 plan 단계로 간다. 슬라이스 밖의 수정이면 work의 \"슬라이스 밖의 수정\" 절차(AC와 R 찾기, spec과 다르면 사용자에게 올리기, check.sh)를 따른다."}}'
    fi ;;
  docs/spec/*)
    s=$(status_of "$proj/$rel")
    case "$s" in
      승인*)
        if approved_plan_exists; then
          echo "차단: 구현 중에는 승인된 spec($rel)을 고치지 않는다. 코드가 옳아 보여도 사용자에게 올린다. 사용자가 코드가 옳다고 정하면 plan의 상태를 승인에서 제안으로 되돌리고, spec을 먼저 고친 뒤 plan의 승인을 다시 받는다(README의 '기준', ADR-0001의 24~26번)." >&2
          exit 2
        fi ;;
    esac ;;
esac
exit 0
