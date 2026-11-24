// commit-msg 훅: Conventional Commits 형식을 검사한다. (docs/rules/git-workflow.md)
import { readFileSync } from 'node:fs';

const file = process.argv[2];
if (!file) {
  console.error('사용법: node scripts/check-commit-msg.mjs <커밋 메시지 파일>');
  process.exit(1);
}

// commit-msg 훅은 git이 주석을 지우기 전에 실행된다. 첫 번째 비어 있지 않은 비주석 줄을 제목으로 본다.
const subject =
  readFileSync(file, 'utf8')
    .split('\n')
    .map((line) => line.trim())
    .find((line) => line && !line.startsWith('#')) ?? '';

// merge·revert·fixup 커밋은 git이 만든 메시지를 그대로 둔다
if (/^(Merge|Revert|fixup!|squash!|amend!) /.test(subject)) process.exit(0);

const TYPES = 'feat|fix|chore|docs|refactor|test|style|perf|ci|build|revert';
if (new RegExp(`^(${TYPES})(\\([^)]+\\))?!?: \\S`).test(subject)) process.exit(0);

console.error(
  [
    `커밋 메시지 형식이 맞지 않습니다: "${subject}"`,
    '형식: <type>: <한국어 요약>  예) feat: 로그인 폼 추가',
    `type: ${TYPES.split('|').join(', ')}`,
    '자세한 규칙: client/docs/rules/git-workflow.md',
  ].join('\n'),
);
process.exit(1);
