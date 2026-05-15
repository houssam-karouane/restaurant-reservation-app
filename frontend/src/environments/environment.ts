/**
 * Default file (tests, SSR prerender, dev builds).
 * Keep `useMockApi` false so unit tests still exercise HttpClient.
 */
export const environment = {
  production: false,
  useMockApi: false,
  apiUrl: '/api/v1',
};
