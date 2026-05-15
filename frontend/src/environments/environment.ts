/**
 * Default file (tests, SSR prerender, dev, production builds without replacement).
 * Keep `useMockApi` false so unit tests still exercise HttpClient.
 * apiUrl is relative `/api/v1` — handled by dev proxy locally and by nginx in Docker/CI.
 */
export const environment = {
  production: false,
  useMockApi: false,
  apiUrl: '/api/v1',
};
