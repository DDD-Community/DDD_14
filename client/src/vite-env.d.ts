/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** API 서버 base URL (예: http://localhost:8080) */
  readonly VITE_API_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
