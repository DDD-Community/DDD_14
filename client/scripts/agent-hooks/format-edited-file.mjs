// PostToolUse(Edit|Write), Claude 전용: 방금 고친 client 파일만 Prettier + oxlint --fix.
// 성공하면 조용히 끝내고, 고치지 못한 lint 오류·경고만 에이전트에게 돌려준다.
import path from 'node:path';
import { outputOf, readInput, repoRoot, run, tail } from './lib.mjs';

const input = readInput();
const clientDir = path.join(repoRoot(input.cwd), 'client');
const file = input.tool_input?.file_path;
if (!file || !path.resolve(file).startsWith(clientDir + path.sep)) process.exit(0);

try {
  run('pnpm', ['exec', 'prettier', '--write', '--ignore-unknown', file], clientDir);
  if (/\.(ts|tsx|js|mjs)$/.test(file)) {
    run('pnpm', ['exec', 'oxlint', '--fix', '--deny-warnings', file], clientDir);
  }
} catch (e) {
  process.stderr.write(tail(outputOf(e), 30));
  process.exit(2); // PostToolUse에서 exit 2 → stderr가 에이전트에게 전달된다
}
