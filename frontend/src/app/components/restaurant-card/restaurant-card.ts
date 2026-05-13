import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

import type { Restaurant } from '../../models/restaurant';

@Component({
  selector: 'app-restaurant-card',
  imports: [CommonModule],
  templateUrl: './restaurant-card.html',
  styleUrl: './restaurant-card.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RestaurantCard {
  @Input({ required: true }) restaurant!: Restaurant;

  priceLabel(priceRange: number | null): string {
    if (priceRange == null || priceRange < 1) {
      return '—';
    }
    return '€'.repeat(Math.min(4, Math.max(1, priceRange)));
  }

  ratingLabel(rating: number | null): string {
    if (rating == null) {
      return '—';
    }
    return rating.toFixed(1);
  }
}
