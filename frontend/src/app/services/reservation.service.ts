import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import type {
  Reservation,
  ReservationCreateRequest,
  ReservationListResponse,
} from '../models/reservation';

const API_URL = 'http://localhost:8000/api/v1';

@Injectable({
  providedIn: 'root',
})
export class ReservationService {
  private readonly http = inject(HttpClient);

  create(payload: ReservationCreateRequest): Observable<Reservation> {
    return this.http.post<Reservation>(`${API_URL}/reservations`, payload);
  }

  listMine(): Observable<ReservationListResponse> {
    return this.http.get<ReservationListResponse>(`${API_URL}/reservations/me`);
  }

  cancel(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${API_URL}/reservations/${id}`);
  }
}
