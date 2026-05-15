/**
 * Render-specific build (activated via `ng build --configuration=render`).
 * apiUrl is absolute because the frontend Static Site on Render cannot reliably
 * proxy /api/v1/* to the backend (Render's rewrite UI sends :splat literally,
 * and _redirects file is not honored). CORS on the backend allows this origin.
 */
export const environment = {
  production: true,
  useMockApi: false,
  apiUrl: 'https://restaurant-api-suqc.onrender.com/api/v1',
};
