import { Injectable, Injector } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '../services/auth.service';

// On injecte Injector au lieu de AuthService directement pour éviter la
// dépendance circulaire AuthService → HttpClient → HTTP_INTERCEPTORS →
// AuthInterceptor → AuthService. Sans ça, le premier appel HTTP émis
// depuis le constructeur de AuthService (typiquement /users/me au boot
// quand un token existe déjà) casse la pipeline d'intercepteurs et
// toutes les requêtes suivantes échouent silencieusement côté Angular.
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private injector: Injector) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const token = this.injector.get(AuthService).getToken();

    if (token) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${token}`,
        },
      });
    }

    return next.handle(request);
  }
}
