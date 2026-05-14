export interface Restaurant {
  id: number;
  name: string;
  address: string | null;
  city: string | null;
  cuisine: string;
  price_range: number | null;
  rating: number | null;
  review_count: number;
  image_url: string | null;
  created_at: string | null;
}

export interface RestaurantListResponse {
  items: Restaurant[];
  total: number;
  page: number;
  pages: number;
}

export interface RestaurantListParams {
  page?: number;
  limit?: number;
  city?: string;
  cuisine?: string;
  min_price?: number;
  max_price?: number;
  min_rating?: number;
}

export interface RestaurantSearchFilters {
  city: string;
  cuisine: string;
  priceRange: number | null;
  minRating: number | null;
}
