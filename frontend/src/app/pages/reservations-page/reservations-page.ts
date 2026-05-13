import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-reservations-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reservations-page.html',
  styleUrl: './reservations-page.css',
})
export class ReservationsPage {
  reservations: any[] = [];
  loading = false;

  constructor() {
    // TODO: Load reservations from API
  }
}
