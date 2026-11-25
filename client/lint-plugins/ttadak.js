// 타닥 FE 전용 lint 규칙 (oxlint JS plugin).
// 메시지에는 "무엇이 틀렸고 어떻게 고치는지"를 쓴다. 에이전트가 그대로 읽고 고친다.

const LAYERS = ['shared', 'features', 'pages', 'app']; // 아래 → 위. 위 레이어만 아래를 import할 수 있다.
const layerOf = (p) => p.match(/(?:^@\/|\/src\/)(shared|features|pages|app)(?:\/|$)/)?.[1];
const featureOf = (p) => p.match(/(?:^@\/|\/src\/)features\/([^/]+)/)?.[1];
const DOC = '(docs/specs/client-architecture.md)';

export default {
  meta: { name: 'ttadak' },
  rules: {
    architecture: {
      create(context) {
        const from = layerOf(context.filename);
        if (!from) return {};
        const fromFeature = featureOf(context.filename);

        const check = (node, src) => {
          if (typeof src !== 'string') return;
          const to = layerOf(src);
          if (!to) return;
          if (LAYERS.indexOf(to) > LAYERS.indexOf(from)) {
            context.report({
              node,
              message: `${from}/에서 ${to}/를 import할 수 없습니다. 의존 방향은 app → pages → features → shared 입니다. ${DOC}`,
            });
          }
          const toFeature = featureOf(src);
          if (!toFeature || toFeature === fromFeature) return;
          if (from === 'features') {
            context.report({
              node,
              message: `features/${fromFeature}에서 features/${toFeature}를 import할 수 없습니다. pages/에서 조립하거나 공통 코드는 shared/로 옮기세요. ${DOC}`,
            });
          } else if (src !== `@/features/${toFeature}`) {
            context.report({
              node,
              message: `feature 내부 파일(${src})을 직접 import하지 말고 '@/features/${toFeature}'(index.ts)로 공개된 것만 쓰세요. ${DOC}`,
            });
          }
        };

        return {
          ImportDeclaration: (node) => check(node, node.source.value),
          ExportNamedDeclaration: (node) => node.source && check(node, node.source.value),
          ExportAllDeclaration: (node) => check(node, node.source.value),
          ImportExpression: (node) => check(node, node.source?.value),
        };
      },
    },
    'no-env-mode': {
      create(context) {
        return {
          MemberExpression(node) {
            const obj = node.object;
            const name = node.property?.name;
            if (
              obj?.type === 'MemberExpression' &&
              obj.object?.type === 'MetaProperty' &&
              obj.property?.name === 'env' &&
              ['MODE', 'PROD', 'DEV'].includes(name)
            ) {
              context.report({
                node,
                message: `import.meta.env.${name} 대신 import.meta.env.VITE_APP_ENV로 분기하세요. (docs/specs/client-tooling.md)`,
              });
            }
          },
        };
      },
    },
  },
};
