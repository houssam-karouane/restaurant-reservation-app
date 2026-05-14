import { RenderMode, ServerRoute } from '@angular/ssr';

// Les routes protégées par authGuard ne doivent PAS être prerenderées :
// au build il n'y a pas d'auth, le guard redirige, et Angular génère un
// HTML statique avec <meta http-equiv="refresh" url="/auth/login">. Au
// runtime nginx sert ce fichier avant même qu'Angular ne boote, et le
// navigateur exécute le refresh → l'utilisateur est éjecté vers /login
// au moindre reload de la page. On force ces routes en CSR pur.
export const serverRoutes: ServerRoute[] = [
  {
    path: 'restaurants',
    renderMode: RenderMode.Server,
  },
  {
    path: 'restaurants/:id',
    renderMode: RenderMode.Server,
  },
  {
    path: 'reservations/me',
    renderMode: RenderMode.Client,
  },
  {
    path: 'profile',
    renderMode: RenderMode.Client,
  },
  {
    path: '**',
    renderMode: RenderMode.Prerender,
  },
];
