import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import type {
  Restaurant,
  RestaurantListParams,
  RestaurantListResponse,
} from '../models/restaurant';
import { environment } from '../../environments/environment';

const API_URL = environment.apiUrl;

@Injectable({
  providedIn: 'root',
})
export class RestaurantService {
  private readonly http = inject(HttpClient);

  list(params: RestaurantListParams = {}): Observable<RestaurantListResponse> {
    let httpParams = new HttpParams();

    if (params.page != null) {
      httpParams = httpParams.set('page', String(params.page));
    }
    if (params.limit != null) {
      httpParams = httpParams.set('limit', String(params.limit));
    }
    if (params.city?.trim()) {
      httpParams = httpParams.set('city', params.city.trim());
    }
    if (params.cuisine?.trim()) {
      httpParams = httpParams.set('cuisine', params.cuisine.trim());
    }
    if (params.min_price != null) {
      httpParams = httpParams.set('min_price', String(params.min_price));
    }
    if (params.max_price != null) {
      httpParams = httpParams.set('max_price', String(params.max_price));
    }
    if (params.min_rating != null) {
      httpParams = httpParams.set('min_rating', String(params.min_rating));
    }

    return this.http.get<RestaurantListResponse>(`${API_URL}/restaurants`, { params: httpParams });
  }

  getById(id: number): Observable<Restaurant> {
    return this.http.get<Restaurant>(`${API_URL}/restaurants/${id}`);
  }
}
