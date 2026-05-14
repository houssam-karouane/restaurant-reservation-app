import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, HTTP_INTERCEPTORS, withInterceptorsFromDi } from '@angular/common/http';

import { routes } from './app.routes';
import { AuthInterceptor } from './interceptors/auth.interceptor';

// NB: pas de provideClientHydration() : le Dockerfile ne sert que le bundle
// browser via nginx, il n'y a pas de runtime SSR pour produire le HTML à
// hydrater. Activer l'hydratation sans SSR bloque les requêtes HTTP au
// boot quand un token est déjà présent dans localStorage (les listes de
// restaurants/réservations restaient vides après reload).
//
// On retire aussi withFetch() : la combinaison fetch + hydratation
// pending-tasks était la cause des appels API silencieusement abandonnés ;
// l'HttpClient XHR par défaut suffit ici.
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(withInterceptorsFromDi()),
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true,
    },
  ],
};
