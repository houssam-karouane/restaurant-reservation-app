import { ChangeDetectionStrategy, Component } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface ReservationRow {
  id: string;
}

@Component({
  selector: 'app-reservations-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reservations-page.html',
  styleUrl: './reservations-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ReservationsPage {
  reservations: ReservationRow[] = [];
  loading = false;

  constructor() {
    // TODO: Load reservations from API
  }

  trackByReservationId(_index: number, item: ReservationRow): string {
    return item.id;
  }
}
