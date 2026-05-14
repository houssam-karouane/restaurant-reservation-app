import type { Reservation } from '../models/reservation';
import type { Restaurant } from '../models/restaurant';

function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function offsetDate(days: number): Date {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d;
}

/** Stable demo restaurants (ids unlikely to collide with a small dev DB). */
export const MOCK_RESTAURANTS: Restaurant[] = [
  {
    id: 9101,
    name: 'Harbor & Hearth',
    address: '120 Bay Street',
    city: 'Portland',
    cuisine: 'Seafood',
    price_range: 3,
    rating: 4.7,
    review_count: 214,
    image_url: null,
    created_at: null,
  },
  {
    id: 9102,
    name: 'Cedar Row Bistro',
    address: '44 Maple Ave',
    city: 'Seattle',
    cuisine: 'French',
    price_range: 4,
    rating: 4.5,
    review_count: 132,
    image_url: null,
    created_at: null,
  },
  {
    id: 9103,
    name: 'Neon Noodle Bar',
    address: '9 Market Lane',
    city: 'Vancouver',
    cuisine: 'Asian fusion',
    price_range: 2,
    rating: 4.8,
    review_count: 401,
    image_url: null,
    created_at: null,
  },
  {
    id: 9104,
    name: 'Olive & Oak',
    address: '300 Hill Road',
    city: 'Portland',
    cuisine: 'Mediterranean',
    price_range: 3,
    rating: 4.4,
    review_count: 98,
    image_url: null,
    created_at: null,
  },
  {
    id: 9105,
    name: 'Smokestack BBQ',
    address: '77 Industrial Way',
    city: 'Austin',
    cuisine: 'Barbecue',
    price_range: 2,
    rating: 4.6,
    review_count: 512,
    image_url: null,
    created_at: null,
  },
  {
    id: 9106,
    name: 'Luna Bakery Café',
    address: '5 Sunrise Sq',
    city: 'Seattle',
    cuisine: 'Café',
    price_range: 1,
    rating: 4.3,
    review_count: 167,
    image_url: null,
    created_at: null,
  },
];

export function mockRecommendationsPick(count = 6): Restaurant[] {
  return MOCK_RESTAURANTS.slice(0, Math.min(count, MOCK_RESTAURANTS.length));
}

export function mockFavoriteRestaurants(): Restaurant[] {
  return [MOCK_RESTAURANTS[0], MOCK_RESTAURANTS[2], MOCK_RESTAURANTS[4]];
}

export function buildMockReservations(): Reservation[] {
  const upcoming1 = offsetDate(5);
  const upcoming2 = offsetDate(12);
  const past1 = offsetDate(-4);
  const past2 = offsetDate(-21);
  const cancelledDay = offsetDate(8);

  return [
    {
      id: 88001,
      restaurant_id: 9101,
      user_id: 1,
      date: isoDate(upcoming1),
      time: '19:00',
      number_of_people: 2,
      status: 'confirmed',
      created_at: null,
    },
    {
      id: 88002,
      restaurant_id: 9103,
      user_id: 1,
      date: isoDate(upcoming2),
      time: '18:30',
      number_of_people: 4,
      status: 'pending',
      created_at: null,
    },
    {
      id: 88003,
      restaurant_id: 9102,
      user_id: 1,
      date: isoDate(cancelledDay),
      time: '20:00',
      number_of_people: 2,
      status: 'cancelled',
      created_at: null,
    },
    {
      id: 88004,
      restaurant_id: 9104,
      user_id: 1,
      date: isoDate(past1),
      time: '19:30',
      number_of_people: 3,
      status: 'confirmed',
      created_at: null,
    },
    {
      id: 88005,
      restaurant_id: 9105,
      user_id: 1,
      date: isoDate(past2),
      time: '12:15',
      number_of_people: 2,
      status: 'confirmed',
      created_at: null,
    },
  ];
}
