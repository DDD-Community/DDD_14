#!/bin/bash
# PreToolUse(Bash): 커밋을 만드는 Bash 명령을 확인한다.
#   - git add -A, git add .: 의도하지 않은 파일이 섞인다. 경로를 지정한다.
#   - git commit: 코드와 문서를 바꾸는 커밋에는 그 스텝의 일지(docs/journal)가 함께 있어야 한다(기록 없는 변경을 막는다).
#   - 일지의 파일 이름은 날짜-이름.md다. git config harness.handle이 있으면 내 이름의 일지만 커밋할 수 있다(다른 사람의 일지를 고치지 않는다).
# 모노레포에서 server/가 프로젝트 폴더다. 경로는 프로젝트 폴더 기준이다(git --relative).
input=$(cat)
tool=$(jq -r '.tool_name // empty' <<<"$input" 2>/dev/null)
[ "$tool" = "Bash" ] || exit 0
cmd=$(jq -r '.tool_input.command // empty' <<<"$input" 2>/dev/null)
cwd=$(jq -r '.cwd // empty' <<<"$input" 2>/dev/null)
proj=${CLAUDE_PROJECT_DIR:-${cwd:-.}}

if grep -Eq '(^|[;&|[:space:]])git add( +-[A-Za-z-]+)* +(-A|--all|\.)( |$)' <<<"$cmd"; then
  echo "차단: git add -A와 git add .는 쓰지 않는다. 경로를 지정해서 스테이징한다." >&2
  exit 2
fi

grep -Eq '(^|[;&|[:space:]])git commit( |$)' <<<"$cmd" || exit 0
staged=$(git -C "$proj" diff --cached --name-only --relative 2>/dev/null)
[ -z "$staged" ] && exit 0

journals=$(grep '^docs/journal/' <<<"$staged")
if grep -Eq '^(src/|docs/(adr|spec|domain|plan|policy)/|\.claude/|scripts/|AGENTS\.md)' <<<"$staged"; then
  if [ -z "$journals" ]; then
    echo "차단: 코드와 문서를 바꾸는 커밋에는 그 스텝의 일지(docs/journal/)가 함께 있어야 한다. 일지를 쓰고 스테이징한 뒤 다시 커밋한다." >&2
    exit 2
  fi
fi

if [ -n "$journals" ]; then
  handle=$(git -C "$proj" config harness.handle 2>/dev/null)
  while IFS= read -r j; do
    name=$(basename "$j")
    if ! grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*\.md$' <<<"$name"; then
      echo "차단: 일지의 파일 이름은 날짜-이름.md다(예: 2026-11-23-seobang.md). 지금: $name" >&2
      exit 2
    fi
    if [ -n "$handle" ] && [[ "$name" != *"-$handle.md" ]]; then
      echo "차단: $name은 다른 사람의 일지다. 내 이름(harness.handle=$handle)의 일지만 커밋한다." >&2
      exit 2
    fi
  done <<<"$journals"
fi
exit 0
