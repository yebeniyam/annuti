import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';
import { User } from '../../types/user';

// Define interface for registration
export interface RegistrationData {
  email: string;
  password: string;
  full_name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

// Define interfaces for login
interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

// Login with credentials
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await axios.post<LoginResponse>(
        `${process.env.REACT_APP_API_URL}/api/v1/auth/login`,
        new URLSearchParams({
          username: credentials.username,
          password: credentials.password,
        }).toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      
      // Store token in localStorage
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      
      // Fetch user profile after successful login
      const profileResponse = await axios.get(`${process.env.REACT_APP_API_URL}/api/v1/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      return {
        user: profileResponse.data,
        token,
      };
      
    } catch (error: any) {
      console.error('Login failed:', error);
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

// Fetch user profile
export const fetchUserProfile = createAsyncThunk(
  'auth/fetchUserProfile',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }
      
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/v1/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      return response.data;
    } catch (error: any) {
      // If there's an error, clear the invalid token
      localStorage.removeItem('token');
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch user profile');
    }
  }
);

// Logout
export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        // Call the logout API if needed
        await axios.post(
          `${process.env.REACT_APP_API_URL}/api/v1/auth/logout`,
          {},
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );
      }
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      // Always remove the token from localStorage
      localStorage.removeItem('token');
      return true;
    }
  }
);

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  loading: false,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state: AuthState) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login cases
      .addCase(login.pending, (state: AuthState) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state: AuthState, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(login.rejected, (state: AuthState, action) => {
        state.loading = false;
        state.error = action.payload as string || 'Failed to login';
        state.token = null;
        state.isAuthenticated = false;
        localStorage.removeItem('token');
      })
      // Fetch user profile cases
      .addCase(fetchUserProfile.pending, (state: AuthState) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.fulfilled, (state: AuthState, action) => {
        state.user = action.payload;
        state.isAuthenticated = true;
        state.loading = false;
        state.error = null;
      })
      .addCase(fetchUserProfile.rejected, (state: AuthState, action) => {
        state.loading = false;
        state.error = action.payload as string || 'Failed to fetch user profile';
        state.user = null;
        state.isAuthenticated = false;
        state.token = null;
        localStorage.removeItem('token');
      })
      // Logout case
      .addCase(logout.pending, (state: AuthState) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(logout.fulfilled, (state: AuthState) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.loading = false;
      })
      .addCase(logout.rejected, (state: AuthState, action) => {
        state.loading = false;
        state.error = action.payload as string || 'Failed to logout';
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;