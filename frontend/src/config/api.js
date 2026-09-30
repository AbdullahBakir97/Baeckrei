// Where the backend lives. In development it runs on its own port; a
// production build talks to the same origin it is served from (see
// DEPLOY.md), unless VITE_API_URL says otherwise.
export const API_URL = (import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:8000' : '')).replace(/\/$/, '')
