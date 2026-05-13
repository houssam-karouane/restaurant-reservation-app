import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { combineLatest } from 'rxjs';

import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-header',
  imports: [CommonModule, RouterLink],
  templateUrl: './header.html',
  styleUrl: './header.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Header {
  private readonly router = inject(Router);
  readonly authService = inject(AuthService);

  readonly headerVm$ = combineLatest({
    isAuthenticated: this.authService.isAuthenticated$,
    currentUser: this.authService.currentUser$,
  });

  logout(): void {
    this.authService.logout();
    void this.router.navigate(['/']);
  }
}
