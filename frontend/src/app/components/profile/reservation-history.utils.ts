import type { Reservation } from '../../models/reservation';

/** Local wall-clock interpretation of API `date` + `time`. */
export function reservationDateTime(res: Reservation): Date {
  const [y, m, d] = res.date.split('-').map(Number);
  const timeParts = res.time.split(':');
  const hh = Number(timeParts[0] ?? 0);
  const mm = Number(timeParts[1] ?? 0);
  return new Date(y, (m || 1) - 1, d || 1, hh, mm, 0, 0);
}

export function isReservationPast(res: Reservation): boolean {
  return reservationDateTime(res).getTime() < Date.now();
}

export type ReservationStatusFilter = 'confirmed' | 'cancelled' | 'past';

export function reservationMatchesFilter(
  res: Reservation,
  filter: ReservationStatusFilter,
): boolean {
  const past = isReservationPast(res);
  if (filter === 'cancelled') {
    return res.status === 'cancelled';
  }
  if (filter === 'past') {
    return past && res.status !== 'cancelled';
  }
  // confirmed tab: upcoming active bookings
  return !past && (res.status === 'confirmed' || res.status === 'pending');
}

export function canCancelReservation(res: Reservation): boolean {
  if (isReservationPast(res) || res.status === 'cancelled') {
    return false;
  }
  return res.status === 'confirmed' || res.status === 'pending';
}
