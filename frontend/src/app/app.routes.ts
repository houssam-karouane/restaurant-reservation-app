import { Routes } from '@angular/router';
import { HomePage } from './pages/home-page/home-page';
import { LoginPage } from './pages/login-page/login-page';
import { RegisterPage } from './pages/register-page/register-page';
import { ProfilePage } from './pages/profile-page/profile-page';
import { ReservationsPage } from './pages/reservations-page/reservations-page';
import { RestaurantsPage } from './pages/restaurants-page/restaurants-page';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    component: HomePage,
  },
  {
    path: 'restaurants',
    component: RestaurantsPage,
  },
  {
    path: 'auth',
    children: [
      {
        path: 'login',
        component: LoginPage,
      },
      {
        path: 'register',
        component: RegisterPage,
      },
    ],
  },
  {
    path: 'profile',
    canActivate: [authGuard],
    component: ProfilePage,
  },
  {
    path: 'reservations/me',
    canActivate: [authGuard],
    component: ReservationsPage,
  },
];
