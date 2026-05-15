import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  Output,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { RouterLink } from '@angular/router';

import { ReviewService } from '../../services/review.service';
import { AuthService } from '../../services/auth.service';
import { ToastService } from '../../services/toast.service';
import type { Review } from '../../models/review';

@Component({
  selector: 'app-add-review',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './add-review.component.html',
  styleUrl: './add-review.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AddReviewComponent {
  private readonly fb = inject(FormBuilder);
  private readonly reviewService = inject(ReviewService);
  private readonly authService = inject(AuthService);
  private readonly toast = inject(ToastService);

  @Input({ required: true }) restaurantId!: number;
  @Output() readonly reviewCreated = new EventEmitter<Review>();

  readonly submitting = signal(false);
  readonly submitError = signal<string | null>(null);
  readonly hoverRating = signal(0);

  readonly form = this.fb.nonNullable.group({
    rating: [0, [Validators.required, Validators.min(1), Validators.max(5)]],
    comment: ['', [Validators.maxLength(500)]],
  });

  readonly stars = [1, 2, 3, 4, 5];

  get isAuthenticated(): boolean {
    return this.authService.isAuthenticated();
  }

  setRating(value: number): void {
    this.form.controls.rating.setValue(value);
    this.form.controls.rating.markAsTouched();
  }

  onSubmit(): void {
    this.submitError.set(null);

    if (!this.isAuthenticated) {
      this.submitError.set('Connectez-vous pour publier un avis.');
      return;
    }

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const raw = this.form.getRawValue();
    const payload = {
      restaurant_id: this.restaurantId,
      rating: raw.rating,
      comment: raw.comment?.trim() || null,
    };

    this.submitting.set(true);
    this.reviewService.create(payload).subscribe({
      next: (review) => {
        this.submitting.set(false);
        this.form.reset({ rating: 0, comment: '' });
        this.toast.success('Avis publié, merci !');
        this.reviewCreated.emit(review);
      },
      error: (err: HttpErrorResponse) => {
        this.submitting.set(false);
        const status = err?.status;
        if (status === 401) {
          this.submitError.set('Votre session a expiré. Reconnectez-vous pour publier.');
          return;
        }
        if (status === 403 || status === 400) {
          // Le backend exige une réservation "completed" pour ce restaurant.
          const detail =
            typeof err?.error?.detail === 'string'
              ? err.error.detail
              : 'Pour publier un avis, vous devez avoir terminé une réservation dans ce restaurant.';
          this.submitError.set(detail);
          return;
        }
        if (status === 409) {
          this.submitError.set('Vous avez déjà publié un avis pour ce restaurant.');
          return;
        }
        const detail =
          typeof err?.error?.detail === 'string'
            ? err.error.detail
            : 'Impossible de publier l’avis. Réessayez dans un instant.';
        this.submitError.set(detail);
      },
    });
  }
}
