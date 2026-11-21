/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 실행 환경. local = 로컬 개발, prod = 프로덕션 */
  readonly VITE_APP_ENV: 'local' | 'prod';
  /** API 서버 base URL */
  readonly VITE_API_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
