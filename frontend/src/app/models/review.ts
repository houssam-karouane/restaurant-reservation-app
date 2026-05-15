export interface Review {
  id: number;
  restaurant_id: number;
  user_id: number;
  rating: number;
  comment: string | null;
  created_at: string | null;
}

export interface ReviewCreateRequest {
  restaurant_id: number;
  rating: number;
  comment?: string | null;
}
