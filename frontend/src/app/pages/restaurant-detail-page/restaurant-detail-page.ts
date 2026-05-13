import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  afterNextRender,
  computed,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { switchMap } from 'rxjs';

import type { Restaurant } from '../../models/restaurant';
import { RestaurantService } from '../../services/restaurant.service';
import { ReservationService } from '../../services/reservation.service';
import { AuthService } from '../../services/auth.service';
import { ToastService } from '../../services/toast.service';
import { Spinner } from '../../components/atoms/spinner/spinner';
import { InlineAlert } from '../../components/atoms/inline-alert/inline-alert';

@Component({
  selector: 'app-restaurant-detail-page',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, Spinner, InlineAlert],
  templateUrl: './restaurant-detail-page.html',
  styleUrl: './restaurant-detail-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RestaurantDetailPage {
  private readonly restaurantService = inject(RestaurantService);
  private readonly reservationService = inject(ReservationService);
  private readonly authService = inject(AuthService);
  private readonly toast = inject(ToastService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);

  readonly restaurant = signal<Restaurant | null>(null);
  readonly loading = signal(true);
  readonly loadError = signal<string | null>(null);

  readonly submitting = signal(false);
  readonly submitError = signal<string | null>(null);

  readonly heroImageFailed = signal(false);

  readonly today = new Date().toISOString().split('T')[0];
  readonly maxDate = this.computeMaxDate();

  readonly form = this.fb.nonNullable.group({
    date: ['', [Validators.required, this.dateNotInPast.bind(this)]],
    time: ['', [Validators.required, this.timeWithinHours.bind(this)]],
    number_of_people: [2, [Validators.required, Validators.min(1), Validators.max(10)]],
  });

  readonly priceLabel = computed(() => {
    const r = this.restaurant();
    const p = r?.price_range;
    if (p == null || p < 1) return '—';
    return '€'.repeat(Math.min(4, Math.max(1, p)));
  });

  readonly ratingLabel = computed(() => {
    const r = this.restaurant();
    return r?.rating != null ? r.rating.toFixed(1) : '—';
  });

  constructor() {
    const destroyRef = inject(DestroyRef);
    afterNextRender(() => {
      this.route.paramMap
        .pipe(
          switchMap((params) => {
            const idRaw = params.get('id');
            const id = idRaw ? Number(idRaw) : NaN;
            this.loading.set(true);
            this.loadError.set(null);
            this.restaurant.set(null);
            if (!Number.isFinite(id) || id <= 0) {
              this.loading.set(false);
              this.loadError.set('Identifiant de restaurant invalide.');
              throw new Error('invalid id');
            }
            return this.restaurantService.getById(id);
          }),
          takeUntilDestroyed(destroyRef),
        )
        .subscribe({
          next: (r) => {
            this.restaurant.set(r);
            this.loading.set(false);
          },
          error: (err: HttpErrorResponse) => {
            this.loading.set(false);
            if (err?.status === 404) {
              this.loadError.set('Ce restaurant est introuvable.');
            } else {
              const detail =
                typeof err?.error?.detail === 'string'
                  ? err.error.detail
                  : 'Impossible de charger le restaurant. Réessayez plus tard.';
              this.loadError.set(detail);
            }
          },
        });
    });
  }

  onSubmit(): void {
    this.submitError.set(null);

    if (!this.authService.isAuthenticated()) {
      const returnUrl = this.router.url;
      this.toast.info('Connectez-vous pour réserver.');
      void this.router.navigate(['/auth/login'], { queryParams: { returnUrl } });
      return;
    }

    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const r = this.restaurant();
    if (!r) return;

    const raw = this.form.getRawValue();
    const payload = {
      restaurant_id: r.id,
      date: raw.date,
      time: raw.time.length === 5 ? `${raw.time}:00` : raw.time,
      number_of_people: Number(raw.number_of_people),
    };

    this.submitting.set(true);
    this.reservationService.create(payload).subscribe({
      next: () => {
        this.submitting.set(false);
        this.toast.success(`Réservation confirmée chez ${r.name}.`);
        void this.router.navigate(['/reservations/me']);
      },
      error: (err: HttpErrorResponse) => {
        this.submitting.set(false);
        if (err?.status === 401) {
          const returnUrl = this.router.url;
          this.toast.info('Votre session a expiré. Reconnectez-vous.');
          void this.router.navigate(['/auth/login'], { queryParams: { returnUrl } });
          return;
        }
        if (err?.status === 409) {
          this.submitError.set(
            'Ce créneau n’est plus disponible. Choisissez une autre date ou heure.',
          );
          return;
        }
        const detail =
          typeof err?.error?.detail === 'string'
            ? err.error.detail
            : 'La réservation a échoué. Réessayez dans quelques instants.';
        this.submitError.set(detail);
      },
    });
  }

  onHeroImageError(): void {
    this.heroImageFailed.set(true);
  }

  /**
   * Construit 4 crops Unsplash distincts à partir de la même URL hero pour
   * peupler la galerie sans nécessiter de table photos côté backend.
   */
  galleryUrls(baseUrl: string): string[] {
    const split = baseUrl.split('?');
    const root = split[0];
    return [
      `${root}?auto=format&fit=crop&w=900&h=600&q=80`,
      `${root}?auto=format&fit=crop&w=600&h=600&q=80&crop=entropy`,
      `${root}?auto=format&fit=crop&w=600&h=600&q=80&crop=faces`,
      `${root}?auto=format&fit=crop&w=600&h=600&q=80&sat=-30`,
    ];
  }

  fieldError(name: 'date' | 'time' | 'number_of_people'): string | null {
    const c = this.form.controls[name];
    if (!c.touched || !c.errors) return null;
    if (c.errors['required']) return 'Champ obligatoire.';
    if (c.errors['min']) return 'Minimum 1 personne.';
    if (c.errors['max']) return 'Maximum 10 personnes.';
    if (c.errors['datePast']) return 'La date doit être aujourd’hui ou plus tard.';
    if (c.errors['timeOutOfHours']) return 'Choisissez un créneau entre 11:00 et 23:00.';
    return 'Valeur invalide.';
  }

  private dateNotInPast(control: AbstractControl): ValidationErrors | null {
    const v = control.value;
    if (!v) return null;
    const picked = new Date(`${v}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return picked.getTime() < today.getTime() ? { datePast: true } : null;
  }

  private timeWithinHours(control: AbstractControl): ValidationErrors | null {
    const v = control.value as string;
    if (!v) return null;
    const [hStr, mStr] = v.split(':');
    const h = Number(hStr);
    const m = Number(mStr ?? '0');
    if (!Number.isFinite(h) || !Number.isFinite(m)) return { timeOutOfHours: true };
    const minutes = h * 60 + m;
    const min = 11 * 60;
    const max = 23 * 60;
    return minutes < min || minutes > max ? { timeOutOfHours: true } : null;
  }

  private computeMaxDate(): string {
    const d = new Date();
    d.setMonth(d.getMonth() + 3);
    return d.toISOString().split('T')[0];
  }
}
