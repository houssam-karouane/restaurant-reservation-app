import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  afterNextRender,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

import type { ProfileUser } from '../../models/user';
import { AuthService } from '../../services/auth.service';
import { Spinner } from '../atoms/spinner/spinner';
import { InlineAlert } from '../atoms/inline-alert/inline-alert';

const API_URL = '/api/v1';

@Component({
  selector: 'app-profile-info',
  standalone: true,
  imports: [CommonModule, Spinner, InlineAlert],
  templateUrl: './profile-info.component.html',
  styleUrl: './profile-info.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfileInfoComponent {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);
  private readonly destroyRef = inject(DestroyRef);

  readonly user = signal<ProfileUser | null>(null);
  readonly loading = signal(true);
  readonly loadError = signal<string | null>(null);

  constructor() {
    afterNextRender(() => {
      this.http
        .get<ProfileUser>(`${API_URL}/users/me`)
        .pipe(takeUntilDestroyed(this.destroyRef))
        .subscribe({
          next: (u) => {
            this.authService.cacheUserProfile(u);
            this.user.set(u);
            this.loadError.set(null);
            this.loading.set(false);
          },
          error: () => {
            const cached = this.authService.getProfileSnapshot();
            this.loading.set(false);
            if (cached) {
              this.user.set(cached);
              this.loadError.set(null);
            } else {
              this.user.set(null);
              this.loadError.set('Could not load your profile.');
            }
          },
        });
    });
  }
}
