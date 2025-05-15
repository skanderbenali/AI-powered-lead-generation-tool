/**
 * Shared type definitions for users and authentication
 */

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  is_active?: boolean;
}

export interface UserUpdate {
  email?: string;
  username?: string;
  full_name?: string;
  password?: string;
  is_active?: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface TokenPayload {
  sub: string;  // username
  id: number;   // user id
  exp: number;  // expiration timestamp
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  notification_emails: boolean;
  dashboard_view: 'grid' | 'list';
}
