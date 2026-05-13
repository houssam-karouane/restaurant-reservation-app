import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

import { RestaurantService } from './restaurant.service';

describe('RestaurantService', () => {
  let service: RestaurantService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(RestaurantService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should GET /restaurants with query params', () => {
    let body: unknown;
    service.list({ page: 2, limit: 5, city: 'Lyon', min_rating: 4 }).subscribe((res) => {
      body = res;
    });

    const req = httpMock.expectOne(
      (request) =>
        request.url === 'http://localhost:8000/api/v1/restaurants' &&
        request.params.get('page') === '2' &&
        request.params.get('limit') === '5' &&
        request.params.get('city') === 'Lyon' &&
        request.params.get('min_rating') === '4',
    );
    expect(req.request.method).toBe('GET');

    const payload = { items: [], total: 0, page: 2, pages: 1 };
    req.flush(payload);
    expect(body).toEqual(payload);
  });

  it('should omit empty optional params', () => {
    service.list({ page: 1 }).subscribe();

    const req = httpMock.expectOne(
      (request) =>
        request.url === 'http://localhost:8000/api/v1/restaurants' &&
        request.params.get('page') === '1' &&
        request.params.keys().length === 1,
    );
    req.flush({ items: [], total: 0, page: 1, pages: 1 });
  });
});
