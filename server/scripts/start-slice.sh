#!/bin/bash
# 슬라이스의 브랜치를 만든다. 사용: scripts/start-slice.sh <이슈번호> <영문-요약> [종류]
# 이름은 <종류>/<이슈번호>-<영문-요약>이다. 종류는 커밋 종류와 같고 기본은 feat다. push하지 않는다.
# 조건: main에 있고, 작업 트리가 깨끗하다. main이 원격의 main보다 뒤처졌으면 fast-forward로 맞춘다.
set -e
num=$1; slug=$2; kind=${3:-feat}
[ -n "$num" ] && [ -n "$slug" ] || { echo "사용: scripts/start-slice.sh <이슈번호> <영문-요약> [종류]" >&2; exit 2; }
case "$kind" in test|file|docs|chore|setting|feat|refactor|fix) ;; *) echo "종류는 test, file, docs, chore, setting, feat, refactor, fix 중 하나다: $kind" >&2; exit 2 ;; esac
[[ "$num" =~ ^[0-9]+$ ]] || { echo "이슈 번호는 숫자여야 한다: $num" >&2; exit 2; }
[[ "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || { echo "영문 요약은 소문자, 숫자, 하이픈이다(예: family-members): $slug" >&2; exit 2; }
proj=${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}
cd "$proj"
cur=$(git branch --show-current)
[ "$cur" = "main" ] || { echo "main에서 시작한다. 지금 브랜치: $cur" >&2; exit 1; }
# 모노레포라 server/ 밖(루트의 .idea/, client/)은 보지 않는다.
[ -z "$(git status --porcelain -- .)" ] || { echo "server/의 작업 트리가 깨끗하지 않다. 먼저 커밋하거나 정리한다." >&2; exit 1; }
if git remote get-url origin >/dev/null 2>&1; then
  git fetch -q origin main
  behind=$(git rev-list --count main..origin/main)
  if [ "$behind" -gt 0 ]; then
    git merge -q --ff-only origin/main
    echo "main을 원격에 맞췄다($behind개 커밋)."
  fi
fi
branch="${kind}/${num}-${slug}"
git show-ref --verify --quiet "refs/heads/$branch" && { echo "이미 있는 브랜치다: $branch" >&2; exit 1; }
git checkout -q -b "$branch"
echo "브랜치를 만들었다: $branch"
