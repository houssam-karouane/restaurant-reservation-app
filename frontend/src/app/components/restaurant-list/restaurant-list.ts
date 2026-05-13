import { ChangeDetectionStrategy, Component, Input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

import type { Restaurant } from '../../models/restaurant';
import { RestaurantCard } from '../restaurant-card/restaurant-card';
import { EmptyState } from '../atoms/empty-state/empty-state';

@Component({
  selector: 'app-restaurant-list',
  imports: [CommonModule, RestaurantCard, EmptyState],
  templateUrl: './restaurant-list.html',
  styleUrl: './restaurant-list.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RestaurantList {
  @Input({ required: true }) restaurants: readonly Restaurant[] = [];
  @Input() page = 1;
  @Input() pages = 1;
  @Input() total = 0;

  readonly pageChange = output<number>();

  goToPage(next: number): void {
    if (next < 1 || next > this.pages) {
      return;
    }
    this.pageChange.emit(next);
  }
}
