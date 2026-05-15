import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import type { Review, ReviewCreateRequest } from '../models/review';
import { environment } from '../../environments/environment';

const API_URL = environment.apiUrl;

@Injectable({ providedIn: 'root' })
export class ReviewService {
  private readonly http = inject(HttpClient);

  create(payload: ReviewCreateRequest): Observable<Review> {
    return this.http.post<Review>(`${API_URL}/reviews/`, payload);
  }

  listForRestaurant(
    restaurantId: number,
    options: { skip?: number; limit?: number } = {},
  ): Observable<Review[]> {
    let params = new HttpParams();
    if (options.skip != null) params = params.set('skip', String(options.skip));
    if (options.limit != null) params = params.set('limit', String(options.limit));
    return this.http.get<Review[]>(`${API_URL}/reviews/restaurant/${restaurantId}`, { params });
  }

  listMine(): Observable<Review[]> {
    return this.http.get<Review[]>(`${API_URL}/reviews/me`);
  }
}
