#!/bin/bash
# PreToolUse(Bash): git push 전에 확인한다.
#   - 보호 브랜치(main)로 가는 push를 막는다. 대상은 refspec의 오른쪽이고, refspec이 없으면 지금 브랜치다.
#   - force 계열(-f, --force, --force-with-lease, --force-if-includes, +refspec)과 --all, --mirror를 막는다.
#   - 현재 커밋을 scripts/check.sh로 검증했는지 확인한다. check.sh가 통과하면 커밋 해시를 기록하고, 기록이 현재 커밋과 다르면 막는다.
# 한계: 별칭, 변수, 셸 함수로 감싼 push와 사람이 터미널에서 직접 하는 push는 보지 못한다(CI와 브랜치 보호의 몫).
#   heredoc 본문 안의 push(예: bash <<EOF로 넘기는 스크립트)도 보지 못한다.
input=$(cat)
tool=$(jq -r '.tool_name // empty' <<<"$input" 2>/dev/null)
[ "$tool" = "Bash" ] || exit 0
cmd=$(jq -r '.tool_input.command // empty' <<<"$input" 2>/dev/null)
cwd=$(jq -r '.cwd // empty' <<<"$input" 2>/dev/null)
proj=${CLAUDE_PROJECT_DIR:-${cwd:-.}}
# heredoc의 본문은 명령이 아니라 글이다(파일에 쓰는 내용, 커밋 메시지). 본문의 줄을 빼고 본다. <<<는 heredoc이 아니다.
code=$(awk -v q="'" '
  BEGIN { re = "(^|[^<])<<-?[ \t]*[\"" q "]?[A-Za-z_][A-Za-z0-9_]*[\"" q "]?" }
  skip { t = $0; if (tabs) sub(/^\t+/, "", t); if (t == delim) skip = 0; next }
  {
    print
    if (match($0, re)) {
      h = substr($0, RSTART, RLENGTH); sub(/^[^<]?<</, "", h)
      tabs = (h ~ /^-/); sub(/^-/, "", h); gsub(/[ \t"]/, "", h); gsub(q, "", h)
      delim = h; skip = 1
    }
  }' <<<"$cmd")
grep -Eq '(^|[;&|[:space:]])git push( |$)' <<<"$code" || exit 0

protected="main"
is_protected() { local b=${1#refs/heads/}; [[ " $protected " == *" $b "* ]]; }
block() { echo "차단: $1 실행하려던 명령: $cmd" >&2; exit 2; }

seg=$(grep -E '(^|[;&|[:space:]])git push( |$)' <<<"$code" | head -1 | sed -E 's/.*(^|[;&|[:space:]])git push( |$)//')
seg=${seg%%[;&|]*}
read -ra words <<<"$(tr -d "\"'" <<<"$seg")"
current=$(git -C "$proj" branch --show-current 2>/dev/null)
positional=()
skip=0
for w in "${words[@]}"; do
  if [ "$skip" = 1 ]; then skip=0; continue; fi
  case "$w" in
    -f|--force|--force-with-lease|--force-with-lease=*|--force-if-includes) block "force push는 하지 않는다." ;;
    --all|--mirror) block "모든 브랜치를 한 번에 push하지 않는다. 브랜치를 지정한다." ;;
    -o|--push-option|--repo|--receive-pack|--exec) skip=1 ;;
    -*) ;;
    *) positional+=("$w") ;;
  esac
done

specs=("${positional[@]:1}")
if [ ${#specs[@]} -eq 0 ]; then
  is_protected "$current" && block "지금 브랜치($current)는 보호 브랜치다. main에는 직접 push하지 않는다."
fi
for spec in "${specs[@]}"; do
  [[ "$spec" == +* ]] && block "force push(+refspec)는 하지 않는다."
  if [[ "$spec" == *:* ]]; then dst=${spec##*:}; else dst=$spec; fi
  [ "$dst" = "HEAD" ] && dst=$current
  is_protected "$dst" && block "main에는 직접 push하지 않는다(대상: ${dst#refs/heads/}). PR로 병합한다."
done

rec=$(git -C "$proj" rev-parse --git-path check-passed 2>/dev/null)
head=$(git -C "$proj" rev-parse HEAD 2>/dev/null)
[ -z "$head" ] && exit 0
[[ "$rec" = /* ]] || rec="$proj/$rec"
if [ ! -f "$rec" ] || [ "$(cat "$rec")" != "$head" ]; then
  echo "차단: 현재 커밋(${head:0:7})을 scripts/check.sh로 검증하지 않았다. check.sh를 통과시킨 뒤 push한다." >&2
  exit 2
fi
exit 0
