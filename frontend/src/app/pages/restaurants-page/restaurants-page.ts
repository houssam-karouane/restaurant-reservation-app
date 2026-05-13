import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, ParamMap } from '@angular/router';
import { distinctUntilChanged, map } from 'rxjs';

import type { Restaurant, RestaurantSearchFilters } from '../../models/restaurant';
import { RestaurantService } from '../../services/restaurant.service';
import { SearchBar } from '../../components/search-bar/search-bar';
import { RestaurantList } from '../../components/restaurant-list/restaurant-list';
import { Spinner } from '../../components/atoms/spinner/spinner';
import { InlineAlert } from '../../components/atoms/inline-alert/inline-alert';

@Component({
  selector: 'app-restaurants-page',
  imports: [CommonModule, SearchBar, RestaurantList, Spinner, InlineAlert],
  templateUrl: './restaurants-page.html',
  styleUrl: './restaurants-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RestaurantsPage {
  private readonly restaurantService = inject(RestaurantService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  private readonly limit = 12;

  readonly filters = signal<RestaurantSearchFilters>({
    city: '',
    cuisine: '',
    priceRange: null,
    minRating: null,
  });
  readonly page = signal(1);

  readonly restaurants = signal<Restaurant[]>([]);
  readonly total = signal(0);
  readonly pages = signal(1);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  constructor() {
    this.route.queryParamMap
      .pipe(
        map((q) => this.parseRoute(q)),
        distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
        takeUntilDestroyed(),
      )
      .subscribe(({ filters, page }) => {
        this.filters.set(filters);
        this.page.set(page);
        this.fetchRestaurants();
      });
  }

  onFiltersChange(filters: RestaurantSearchFilters): void {
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        city: filters.city || undefined,
        cuisine: filters.cuisine || undefined,
        price: filters.priceRange ?? undefined,
        min_rating: filters.minRating ?? undefined,
        page: undefined,
      },
    });
  }

  onPageChange(page: number): void {
    const f = this.filters();
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        city: f.city || undefined,
        cuisine: f.cuisine || undefined,
        price: f.priceRange ?? undefined,
        min_rating: f.minRating ?? undefined,
        page: page <= 1 ? undefined : page,
      },
    });
  }

  private parseRoute(q: ParamMap): { filters: RestaurantSearchFilters; page: number } {
    const priceRaw = q.get('price');
    const ratingRaw = q.get('min_rating');
    const priceNum = priceRaw != null && priceRaw !== '' ? Number(priceRaw) : null;
    const ratingNum = ratingRaw != null && ratingRaw !== '' ? Number(ratingRaw) : null;

    return {
      filters: {
        city: q.get('city')?.trim() ?? '',
        cuisine: q.get('cuisine')?.trim() ?? '',
        priceRange: priceNum != null && Number.isFinite(priceNum) ? priceNum : null,
        minRating: ratingNum != null && Number.isFinite(ratingNum) ? ratingNum : null,
      },
      page: Math.max(1, parseInt(q.get('page') ?? '1', 10) || 1),
    };
  }

  private fetchRestaurants(): void {
    this.loading.set(true);
    this.error.set(null);
    const f = this.filters();
    this.restaurantService
      .list({
        page: this.page(),
        limit: this.limit,
        city: f.city || undefined,
        cuisine: f.cuisine || undefined,
        min_price: f.priceRange ?? undefined,
        max_price: f.priceRange ?? undefined,
        min_rating: f.minRating ?? undefined,
      })
      .subscribe({
        next: (res) => {
          this.loading.set(false);
          this.restaurants.set(res.items);
          this.total.set(res.total);
          this.pages.set(res.pages);
        },
        error: (err: { error?: { detail?: unknown } }) => {
          this.loading.set(false);
          this.restaurants.set([]);
          this.total.set(0);
          this.pages.set(1);
          const detail = err?.error?.detail;
          const message =
            typeof detail === 'string' ? detail : 'Could not load restaurants. Is the API running?';
          this.error.set(message);
        },
      });
  }
}
