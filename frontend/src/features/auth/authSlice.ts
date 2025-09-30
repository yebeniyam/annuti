import { createSlice, createAsyncThunk, PayloadAction, Draft } from '@reduxjs/toolkit';
import axios from 'axios';
import { User, AuthUser } from '../../types/user';

// Define interface for registration
export interface RegistrationData {
  email: string;
  password: string;
  full_name: string;
}

// Define interfaces for login
interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Auth state interface
interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

// Register new user
export const register = createAsyncThunk<
  { access_token: string; token_type: string; user: AuthUser },
  RegistrationData,
  { rejectValue: string }
>(
  'auth/register',
  async (userData: RegistrationData, { rejectWithValue }) => {
    try {
      // Register the user
      await axios.post(
        `${process.env.REACT_APP_API_URL}/api/v1/auth/register`,
        userData
      );
      
      // Automatically log in the user after registration
      const loginResponse = await axios.post<{
        access_token: string;
        token_type: string;
        user: AuthUser;
      }>(
        `${process.env.REACT_APP_API_URL}/api/v1/auth/login`,
        new URLSearchParams({
          username: userData.email,
          password: userData.password,
          grant_type: 'password',
        }).toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      
      const { access_token, token_type, user } = loginResponse.data;
      
      if (!access_token || !user) {
        return rejectWithValue('Invalid response from server after registration');
      }
      
      // Store token in localStorage
      localStorage.setItem('token', access_token);
      
      // Create AuthUser object
      const authUser: AuthUser = {
        id: user.id,
        email: user.email,
        full_name: user.full_name || userData.full_name || user.email.split('@')[0],
        is_superuser: user.is_superuser || false,
        role: user.role || 'user',
      };
      
      return {
        access_token,
        token_type,
        user: authUser,
      };
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Registration failed. Please try again.'
      );
    }
  }
);

// Login user
export const login = createAsyncThunk<
  { access_token: string; token_type: string; user: AuthUser },
  LoginCredentials,
  { rejectValue: string }
>(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await axios.post<{
        access_token: string;
        token_type: string;
        user: AuthUser;
      }>(
        `${process.env.REACT_APP_API_URL}/api/v1/auth/login`,
        new URLSearchParams({
          username: credentials.username,
          password: credentials.password,
          grant_type: 'password',
        }).toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          timeout: 10000, // 10 seconds timeout
        }
      );
      
      const { access_token, token_type, user } = response.data;
      
      if (!access_token || !user) {
        return rejectWithValue('Invalid response from server');
      }
      
      // Store token in localStorage
      localStorage.setItem('token', access_token);
      
      // Ensure we have a valid AuthUser object
      const authUser: AuthUser = {
        id: user.id,
        email: user.email,
        full_name: user.full_name || user.email.split('@')[0],
        is_superuser: user.is_superuser || false,
        role: user.role || 'user',
      };
      
      return {
        access_token,
        token_type,
        user: authUser,
      };
    } catch (error: any) {
      console.error('Login error:', error);
      let errorMessage = 'Login failed. Please check your credentials.';
      
      if (error.response) {
        // Server responded with an error
        errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage;
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'No response from server. Please check your connection.';
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Request timeout. Please try again.';
      }
      
      return rejectWithValue(errorMessage);
    }
  }
);

// Logout user
export const logout = createAsyncThunk<void, void, { rejectValue: string }>(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      // Clear token from localStorage
      localStorage.removeItem('token');
      
      // Optional: Call logout endpoint if needed
      try {
        await axios.post(`${process.env.REACT_APP_API_URL}/api/v1/auth/logout`, {}, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
      } catch (error) {
        console.warn('Logout API call failed, but continuing with local logout:', error);
      }
    } catch (error: any) {
      return rejectWithValue('Failed to logout');
    }
  }
);

// Fetch user profile
export const fetchUserProfile = createAsyncThunk<
  AuthUser,
  void,
  { rejectValue: string }
>(
  'auth/fetchUserProfile',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue('No authentication token found');
      }

      const response = await axios.get<User>(
        `${process.env.REACT_APP_API_URL}/api/v1/users/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const user = response.data;
      return {
        id: user.id,
        email: user.email,
        full_name: user.full_name || user.email.split('@')[0],
        is_superuser: (user as any).is_superuser || false,
        role: user.role || 'user',
      };
    } catch (error: any) {
      // If unauthorized, clear the token
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
      }
      
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to fetch user profile'
      );
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
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Handle login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access_token;
        state.user = action.payload.user;
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      })
      
      // Handle registration
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access_token;
        state.user = action.payload.user;
        state.error = null;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Registration failed';
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
      })
      
      // Handle logout
      .addCase(logout.fulfilled, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.error = null;
      })
      .addCase(logout.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Handle fetch user profile
      .addCase(fetchUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = action.payload as string;
        localStorage.removeItem('token');
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;