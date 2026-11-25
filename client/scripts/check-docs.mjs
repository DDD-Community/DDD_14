// 문서 정합성 검사 (pnpm docs:check). 규칙: docs/rules/documentation.md
//   1. 문서 안 상대 링크가 실제 파일을 가리키는지
//   2. ADR 파일명·번호 형식과 중복 (두 사람이 같은 번호를 쓰는 경우)
//   3. plan 파일명의 날짜 접두어
//   4. 환경 변수: .env* 파일 · src/vite-env.d.ts · specs/client-tooling.md 표가 일치하는지
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const clientDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const docsDir = path.join(clientDir, 'docs');
const rel = (p) => path.relative(clientDir, p);
const problems = [];

const walk = (dir) =>
  readdirSync(dir).flatMap((name) => {
    const p = path.join(dir, name);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });

// 1. 상대 링크 (코드 블록 안은 예시이므로 건너뛴다)
const repoRoot = path.resolve(clientDir, '..');
const skillsDir = path.join(repoRoot, '.agents/skills');
const lockPath = path.join(repoRoot, 'skills-lock.json');
const externalSkills = new Set([
  'playwright-cli', // playwright-cli install --skills 로 설치
  ...Object.keys(existsSync(lockPath) ? JSON.parse(readFileSync(lockPath, 'utf8')).skills : {}),
]);
const teamSkillFiles = existsSync(skillsDir)
  ? readdirSync(skillsDir)
      .filter((name) => !externalSkills.has(name))
      .map((name) => path.join(skillsDir, name, 'SKILL.md'))
  : [];
const markdownFiles = [
  ...walk(docsDir),
  path.join(clientDir, 'AGENTS.md'),
  path.join(clientDir, 'CLAUDE.md'),
  path.join(clientDir, 'README.md'),
  path.join(repoRoot, 'AGENTS.md'),
  ...teamSkillFiles,
].filter((p) => p.endsWith('.md') && existsSync(p));
for (const file of markdownFiles) {
  const text = readFileSync(file, 'utf8').replace(/^(`{3,}|~{3,})[^\n]*\n[\s\S]*?^\1\s*$/gm, '');
  for (const [, target] of text.matchAll(/\[[^\]]*\]\(([^)\s]+)\)/g)) {
    if (/^(https?:|mailto:|#)/.test(target)) continue;
    let resolved;
    try {
      resolved = path.resolve(path.dirname(file), decodeURI(target.split('#')[0]));
    } catch {
      problems.push(`${rel(file)}: 링크 주소를 해석할 수 없습니다 → ${target}`);
      continue;
    }
    if (!existsSync(resolved)) problems.push(`${rel(file)}: 깨진 링크 → ${target}`);
  }
}

// 2. ADR 파일명과 번호
const adrDir = path.join(docsDir, 'adr');
const adrNumbers = new Map();
for (const name of (existsSync(adrDir) ? readdirSync(adrDir) : []).filter(
  (n) => !n.startsWith('.'),
)) {
  const match = name.match(/^(\d{4})-[a-z0-9-]+\.md$/);
  if (!match) {
    problems.push(`docs/adr/${name}: 파일명은 NNNN-<주제>.md 형식이어야 합니다`);
    continue;
  }
  const [, number] = match;
  if (adrNumbers.has(number)) {
    problems.push(
      `docs/adr/${name}: ADR 번호 ${number}가 ${adrNumbers.get(number)}와 겹칩니다. 나중에 머지하는 쪽이 번호를 바꾸세요`,
    );
  }
  adrNumbers.set(number, name);
  const title = readFileSync(path.join(adrDir, name), 'utf8').split('\n')[0];
  if (!title.startsWith(`# ${number}.`)) {
    problems.push(`docs/adr/${name}: 제목은 "# ${number}. <주제>"로 시작해야 합니다`);
  }
}

// 3. plan 파일명
const plansDir = path.join(docsDir, 'plans');
for (const name of (existsSync(plansDir) ? readdirSync(plansDir) : []).filter(
  (n) => !n.startsWith('.'),
)) {
  if (!/^\d{4}-\d{2}-\d{2}-.+\.md$/.test(name)) {
    problems.push(`docs/plans/${name}: 파일명은 YYYY-MM-DD-<주제>.md 형식이어야 합니다`);
  }
}

// 4. 환경 변수
const envVars = new Set();
for (const name of readdirSync(clientDir).filter(
  (n) => /^\.env(\..+)?$/.test(n) && !n.endsWith('.local'),
)) {
  for (const [, key] of readFileSync(path.join(clientDir, name), 'utf8').matchAll(
    /^(VITE_\w+)=/gm,
  )) {
    envVars.add(key);
  }
}
const typeVars = new Set(
  [
    ...readFileSync(path.join(clientDir, 'src/vite-env.d.ts'), 'utf8').matchAll(
      /readonly (VITE_\w+)/g,
    ),
  ].map((m) => m[1]),
);
const specVars = new Set(
  [
    ...readFileSync(path.join(docsDir, 'specs/client-tooling.md'), 'utf8').matchAll(
      /^\| `(VITE_\w+)`/gm,
    ),
  ].map((m) => m[1]),
);
const sources = [
  { name: '.env* 파일', keys: envVars },
  { name: 'src/vite-env.d.ts', keys: typeVars },
  { name: 'docs/specs/client-tooling.md 변수 표', keys: specVars },
];
for (const key of new Set([...envVars, ...typeVars, ...specVars])) {
  const missing = sources.filter(({ keys }) => !keys.has(key)).map(({ name }) => name);
  if (missing.length) problems.push(`환경 변수 ${key}: ${missing.join(', ')}에 없습니다`);
}

if (problems.length) {
  console.error(
    `문서 검사 실패 (${problems.length}건)\n${problems.map((p) => `- ${p}`).join('\n')}`,
  );
  process.exit(1);
}
console.log('문서 검사 통과');
