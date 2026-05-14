export type ReservationStatus = 'pending' | 'confirmed' | 'cancelled';

export interface Reservation {
  id: number;
  restaurant_id: number;
  user_id: number;
  date: string;
  time: string;
  number_of_people: number;
  status: ReservationStatus;
  created_at: string | null;
}

export interface ReservationCreateRequest {
  restaurant_id: number;
  date: string;
  time: string;
  number_of_people: number;
}

export interface ReservationListResponse {
  items: Reservation[];
  total: number;
}
