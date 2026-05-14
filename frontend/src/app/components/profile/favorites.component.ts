import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  afterNextRender,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

import type { Restaurant } from '../../models/restaurant';
import { mockFavoriteRestaurants } from '../../data/profile-mocks';
import { Spinner } from '../atoms/spinner/spinner';
import { InlineAlert } from '../atoms/inline-alert/inline-alert';

const API_URL = '/api/v1';

interface FavoriteListResponse {
  items: Restaurant[];
}

@Component({
  selector: 'app-favorites',
  standalone: true,
  imports: [CommonModule, RouterLink, Spinner, InlineAlert],
  templateUrl: './favorites.component.html',
  styleUrl: './favorites.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FavoritesComponent {
  private readonly http = inject(HttpClient);
  private readonly destroyRef = inject(DestroyRef);

  readonly restaurants = signal<Restaurant[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  constructor() {
    afterNextRender(() => {
      this.http
        .get<FavoriteListResponse>(`${API_URL}/users/me/favorites`)
        .pipe(
          map((res) => res.items ?? []),
          catchError(() => of(mockFavoriteRestaurants())),
          takeUntilDestroyed(this.destroyRef),
        )
        .subscribe({
          next: (items) => {
            this.restaurants.set(items);
            this.loading.set(false);
          },
          error: () => {
            this.loading.set(false);
            this.error.set('Could not load favorites.');
          },
        });
    });
  }
}
