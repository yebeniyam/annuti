// Define types that might be shared across the application

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  is_superuser?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface AuthUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_superuser: boolean;
}