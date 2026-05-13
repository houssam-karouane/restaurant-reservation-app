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
import { forkJoin, of, switchMap } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

import { ReservationService } from '../../services/reservation.service';
import { RestaurantService } from '../../services/restaurant.service';
import { Spinner } from '../../components/atoms/spinner/spinner';
import { InlineAlert } from '../../components/atoms/inline-alert/inline-alert';
import type { Reservation } from '../../models/reservation';
import type { Restaurant } from '../../models/restaurant';

interface ReservationRow {
  reservation: Reservation;
  restaurant: Restaurant | null;
}

@Component({
  selector: 'app-reservations-page',
  standalone: true,
  imports: [CommonModule, Spinner, InlineAlert],
  templateUrl: './reservations-page.html',
  styleUrl: './reservations-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReservationsPage {
  private readonly reservationService = inject(ReservationService);
  private readonly restaurantService = inject(RestaurantService);

  readonly rows = signal<ReservationRow[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  constructor() {
    const destroyRef = inject(DestroyRef);
    afterNextRender(() => {
      this.reservationService
        .listMine()
        .pipe(
          switchMap((res) => {
            if (res.items.length === 0) return of<ReservationRow[]>([]);
            const lookups = res.items.map((r) =>
              this.restaurantService.getById(r.restaurant_id).pipe(
                map((restaurant) => ({ reservation: r, restaurant }) as ReservationRow),
                catchError(() => of({ reservation: r, restaurant: null } as ReservationRow)),
              ),
            );
            return forkJoin(lookups);
          }),
          takeUntilDestroyed(destroyRef),
        )
        .subscribe({
          next: (rows) => {
            this.rows.set(rows);
            this.loading.set(false);
          },
          error: () => {
            this.loading.set(false);
            this.error.set('Impossible de charger vos réservations.');
          },
        });
    });
  }

  statusLabel(status: string): string {
    switch (status) {
      case 'confirmed':
        return 'Confirmée';
      case 'pending':
        return 'En attente';
      case 'cancelled':
        return 'Annulée';
      default:
        return status;
    }
  }
}
