import axios from 'axios';

/** 모든 API 요청은 이 인스턴스를 쓴다. */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10_000,
});
