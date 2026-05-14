/** Public profile fields from `GET /users/me` (may include extra keys from the API). */
export interface ProfileUser {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active?: boolean;
  created_at?: string | null;
}
