import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  Input,
  OnChanges,
  SimpleChanges,
  afterNextRender,
  computed,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';

import { ReviewService } from '../../services/review.service';
import type { Review } from '../../models/review';
import { Spinner } from '../atoms/spinner/spinner';
import { InlineAlert } from '../atoms/inline-alert/inline-alert';

@Component({
  selector: 'app-reviews-list',
  standalone: true,
  imports: [CommonModule, Spinner, InlineAlert],
  templateUrl: './reviews-list.component.html',
  styleUrl: './reviews-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReviewsListComponent implements OnChanges {
  private readonly reviewService = inject(ReviewService);
  private readonly destroyRef = inject(DestroyRef);

  @Input({ required: true }) restaurantId!: number;
  /** Compteur que le parent peut incrémenter pour forcer un refetch. */
  @Input() reloadKey = 0;

  readonly reviews = signal<Review[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly hasReviews = computed(() => this.reviews().length > 0);

  constructor() {
    afterNextRender(() => this.fetch());
  }

  ngOnChanges(changes: SimpleChanges): void {
    // Sur changement de restaurantId OU de reloadKey on rafraichit.
    if (changes['restaurantId'] || changes['reloadKey']) {
      // afterNextRender a déjà lancé un fetch au tout premier render ;
      // ngOnChanges gère les rafraichissements ultérieurs.
      if (!changes['restaurantId']?.firstChange || changes['reloadKey']) {
        this.fetch();
      }
    }
  }

  starsArray(rating: number): number[] {
    const safe = Math.max(0, Math.min(5, Math.round(rating)));
    return Array.from({ length: 5 }, (_, i) => (i < safe ? 1 : 0));
  }

  private fetch(): void {
    if (!this.restaurantId) return;
    this.loading.set(true);
    this.error.set(null);
    this.reviewService
      .listForRestaurant(this.restaurantId, { limit: 20 })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (items) => {
          this.reviews.set(items ?? []);
          this.loading.set(false);
        },
        error: () => {
          this.loading.set(false);
          this.error.set('Impossible de charger les avis pour le moment.');
        },
      });
  }
}
