import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

import { SearchBar } from '../../components/search-bar/search-bar';
import type { RestaurantSearchFilters } from '../../models/restaurant';

@Component({
  selector: 'app-home-page',
  imports: [CommonModule, RouterLink, SearchBar],
  templateUrl: './home-page.html',
  styleUrl: './home-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomePage {
  private readonly router = inject(Router);

  readonly heroSearchDefaults: RestaurantSearchFilters = {
    city: '',
    cuisine: '',
    priceRange: null,
    minRating: null,
  };

  readonly featuredRestaurantIds: readonly number[] = [1, 2, 3, 4, 5, 6];

  trackByRestaurantId(_index: number, id: number): number {
    return id;
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
