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
import { of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

import { RestaurantService } from '../../services/restaurant.service';
import type { Restaurant } from '../../models/restaurant';
import { mockRecommendationsPick } from '../../data/profile-mocks';
import { Spinner } from '../atoms/spinner/spinner';
import { InlineAlert } from '../atoms/inline-alert/inline-alert';

@Component({
  selector: 'app-recommendations',
  standalone: true,
  imports: [CommonModule, RouterLink, Spinner, InlineAlert],
  templateUrl: './recommendations.component.html',
  styleUrl: './recommendations.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RecommendationsComponent {
  private readonly restaurantService = inject(RestaurantService);
  private readonly destroyRef = inject(DestroyRef);

  readonly restaurants = signal<Restaurant[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  constructor() {
    afterNextRender(() => {
      this.restaurantService
        .list({ page: 1, limit: 6 })
        .pipe(
          map((res) => res.items.slice(0, 6)),
          catchError(() => of(mockRecommendationsPick(6))),
          takeUntilDestroyed(this.destroyRef),
        )
        .subscribe({
          next: (items) => {
            const pick = items.length >= 4 ? items.slice(0, 6) : mockRecommendationsPick(6);
            this.restaurants.set(pick);
            this.loading.set(false);
          },
          error: () => {
            this.loading.set(false);
            this.error.set('Could not load recommendations.');
          },
        });
    });
  }
}
