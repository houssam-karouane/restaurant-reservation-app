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
import { forkJoin, of } from 'rxjs';
import { catchError, map, switchMap } from 'rxjs/operators';

import { ReservationService } from '../../services/reservation.service';
import { RestaurantService } from '../../services/restaurant.service';
import { Spinner } from '../atoms/spinner/spinner';
import { InlineAlert } from '../atoms/inline-alert/inline-alert';
import type { Reservation } from '../../models/reservation';
import type { Restaurant } from '../../models/restaurant';
import { buildMockReservations, MOCK_RESTAURANTS } from '../../data/profile-mocks';
import {
  canCancelReservation,
  reservationMatchesFilter,
  type ReservationStatusFilter,
} from './reservation-history.utils';

export interface ReservationRow {
  reservation: Reservation;
  restaurant: Restaurant | null;
}

@Component({
  selector: 'app-reservation-history',
  standalone: true,
  imports: [CommonModule, Spinner, InlineAlert],
  templateUrl: './reservation-history.component.html',
  styleUrl: './reservation-history.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReservationHistoryComponent {
  private readonly reservationService = inject(ReservationService);
  private readonly restaurantService = inject(RestaurantService);
  private readonly destroyRef = inject(DestroyRef);

  /** True when `listMine` failed and the UI is showing demo reservations. */
  private listSourceMock = false;

  readonly filters: { id: ReservationStatusFilter; label: string }[] = [
    { id: 'confirmed', label: 'Confirmed' },
    { id: 'cancelled', label: 'Cancelled' },
    { id: 'past', label: 'Past' },
  ];

  readonly activeFilter = signal<ReservationStatusFilter>('confirmed');
  readonly rows = signal<ReservationRow[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly cancelError = signal<string | null>(null);
  readonly cancellingId = signal<number | null>(null);

  readonly filteredRows = computed(() => {
    const f = this.activeFilter();
    return this.rows().filter((row) => reservationMatchesFilter(row.reservation, f));
  });

  constructor() {
    afterNextRender(() => this.loadReservations());
  }

  setFilter(id: ReservationStatusFilter): void {
    this.activeFilter.set(id);
    this.cancelError.set(null);
  }

  statusLabel(status: string): string {
    switch (status) {
      case 'confirmed':
        return 'Confirmed';
      case 'pending':
        return 'Pending';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  canCancel(row: ReservationRow): boolean {
    return canCancelReservation(row.reservation);
  }

  confirmCancel(row: ReservationRow): void {
    if (!this.canCancel(row)) return;
    const name = row.restaurant?.name ?? `Restaurant #${row.reservation.restaurant_id}`;
    if (!confirm(`Cancel your reservation at ${name} on ${row.reservation.date}?`)) {
      return;
    }
    this.cancelError.set(null);
    if (this.listSourceMock) {
      this.cancellingId.set(row.reservation.id);
      this.rows.update((rows) =>
        rows.map((r) =>
          r.reservation.id === row.reservation.id
            ? {
                ...r,
                reservation: { ...r.reservation, status: 'cancelled' },
              }
            : r,
        ),
      );
      this.cancellingId.set(null);
      return;
    }

    this.cancellingId.set(row.reservation.id);
    this.reservationService
      .cancel(row.reservation.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.cancellingId.set(null);
          this.loadReservations();
        },
        error: () => {
          this.cancellingId.set(null);
          this.cancelError.set('Could not cancel this reservation. Please try again.');
        },
      });
  }

  private loadReservations(): void {
    this.loading.set(true);
    this.error.set(null);
    let usedMockList = false;
    this.reservationService
      .listMine()
      .pipe(
        catchError(() => {
          usedMockList = true;
          const items = buildMockReservations();
          return of({ items, total: items.length });
        }),
        switchMap((res) => {
          if (res.items.length === 0) return of<ReservationRow[]>([]);
          const lookups = res.items.map((r) =>
            this.restaurantService.getById(r.restaurant_id).pipe(
              map((restaurant) => ({ reservation: r, restaurant }) as ReservationRow),
              catchError(() => {
                const mock = MOCK_RESTAURANTS.find((m) => m.id === r.restaurant_id) ?? null;
                return of({ reservation: r, restaurant: mock } as ReservationRow);
              }),
            ),
          );
          return forkJoin(lookups);
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (list) => {
          this.listSourceMock = usedMockList;
          this.rows.set(list);
          this.loading.set(false);
        },
        error: () => {
          this.loading.set(false);
          this.error.set('Could not load reservations.');
        },
      });
  }
}
