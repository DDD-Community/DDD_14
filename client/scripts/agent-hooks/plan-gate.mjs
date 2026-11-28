// PreToolUse(Edit|Write), Claude 전용: plan 없이 client/src를 고치려 하면 막고
// client-new-feature 스킬로 안내한다. plan 파일을 작업 중(수정·삭제)이어도 plan이 있는 것으로 본다.
// 끄기: TTADAK_PLAN_GATE=0
import path from 'node:path';
import { activePlans, block, git, readInput, repoRoot, skill } from './lib.mjs';

if (process.env.TTADAK_PLAN_GATE === '0') process.exit(0);
const input = readInput();
const root = repoRoot(input.cwd);
const file = path.resolve(root, input.tool_input?.file_path ?? '');
if (!file.startsWith(path.join(root, 'client', 'src') + path.sep)) process.exit(0);
if (activePlans(root).length) process.exit(0);
if (git(['status', '--porcelain', '-z', '--', 'client/docs/plans'], root).length) process.exit(0);

block(
  `진행 중인 plan이 없습니다. ${skill('client-new-feature')} 절차대로 client/docs/plans/에 plan(- 상태: 진행 중)을 먼저 쓰고 구현하세요. 작은 수정이면 짧은 plan이면 됩니다.`,
);
