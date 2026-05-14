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
import { Router, RouterLink } from '@angular/router';

import { SearchBar } from '../../components/search-bar/search-bar';
import { RestaurantCard } from '../../components/restaurant-card/restaurant-card';
import { Spinner } from '../../components/atoms/spinner/spinner';
import { InlineAlert } from '../../components/atoms/inline-alert/inline-alert';
import { RevealSectionDirective } from '../../directives/reveal-section';
import type { Restaurant, RestaurantSearchFilters } from '../../models/restaurant';
import { RestaurantService } from '../../services/restaurant.service';

@Component({
  selector: 'app-home-page',
  imports: [CommonModule, RouterLink, SearchBar, RestaurantCard, Spinner, InlineAlert, RevealSectionDirective],
  templateUrl: './home-page.html',
  styleUrl: './home-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomePage {
  private readonly router = inject(Router);
  private readonly restaurantService = inject(RestaurantService);

  readonly heroSearchDefaults: RestaurantSearchFilters = {
    city: '',
    cuisine: '',
    priceRange: null,
    minRating: null,
  };

  readonly featured = signal<Restaurant[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  constructor() {
    const destroyRef = inject(DestroyRef);
    afterNextRender(() => {
      this.restaurantService
        .list({ page: 1, limit: 6, min_rating: 4 })
        .pipe(takeUntilDestroyed(destroyRef))
        .subscribe({
          next: (res) => {
            this.featured.set(res.items);
            this.loading.set(false);
          },
          error: () => {
            this.loading.set(false);
            this.error.set('Impossible de charger les restaurants. L’API est-elle démarrée ?');
          },
        });
    });
  }

  onHeroSearch(filters: RestaurantSearchFilters): void {
    void this.router.navigate(['/restaurants'], {
      queryParams: {
        city: filters.city || undefined,
        cuisine: filters.cuisine || undefined,
        price: filters.priceRange ?? undefined,
        min_rating: filters.minRating ?? undefined,
      },
    });
  }
}
