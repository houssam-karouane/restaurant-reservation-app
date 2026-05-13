import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RestaurantCard } from './restaurant-card';
import type { Restaurant } from '../../models/restaurant';

describe('RestaurantCard', () => {
  let fixture: ComponentFixture<RestaurantCard>;

  const mockRestaurant: Restaurant = {
    id: 1,
    name: 'Test Bistro',
    address: '1 Rue Test',
    city: 'Paris',
    cuisine: 'française',
    price_range: 2,
    rating: 4.5,
    review_count: 12,
    created_at: null,
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RestaurantCard],
    }).compileComponents();

    fixture = TestBed.createComponent(RestaurantCard);
    fixture.componentInstance.restaurant = mockRestaurant;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should render name, rating, cuisine, and price', () => {
    const text = fixture.nativeElement.textContent as string;
    expect(text).toContain('Test Bistro');
    expect(text).toContain('4.5');
    expect(text).toContain('française');
    expect(text).toContain('€€');
    expect(text).toContain('Paris');
    expect(text).toContain('12');
  });
});
