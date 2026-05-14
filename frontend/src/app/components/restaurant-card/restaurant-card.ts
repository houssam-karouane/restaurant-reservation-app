import { ChangeDetectionStrategy, Component, Input, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

import type { Restaurant } from '../../models/restaurant';

@Component({
  selector: 'app-restaurant-card',
  imports: [CommonModule, RouterLink],
  templateUrl: './restaurant-card.html',
  styleUrl: './restaurant-card.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RestaurantCard {
  @Input({ required: true }) restaurant!: Restaurant;

  readonly imageFailed = signal(false);

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

  onImageError(): void {
    this.imageFailed.set(true);
  }
}
