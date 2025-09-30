import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { User } from '../../types/user';

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
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

// Register new user
export const register = createAsyncThunk<
  { access_token: string; token_type: string; user: User },
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
      }>(
        `${process.env.REACT_APP_API_URL}/api/v1/auth/login`,
        new URLSearchParams({
          username: userData.email,
          password: userData.password,
        }).toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      
      // Store token in localStorage
      const token = loginResponse.data.access_token;
      localStorage.setItem('token', token);
      
      // Get user profile
      const userResponse = await axios.get<User>(
        `${process.env.REACT_APP_API_URL}/api/v1/users/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      
      return {
        access_token: token,
        token_type: loginResponse.data.token_type,
        user: userResponse.data,
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
  { access_token: string; token_type: string; user: User },
  LoginCredentials,
  { rejectValue: string }
>(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      const response = await axios.post<{
        access_token: string;
        token_type: string;
      }>(
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
      
      // Get user profile
      const userResponse = await axios.get<User>(
        `${process.env.REACT_APP_API_URL}/api/v1/users/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      
      return {
        access_token: token,
        token_type: response.data.token_type,
        user: userResponse.data,
      };
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Login failed. Please check your credentials.'
      );
    }
  }
);

// Logout user
export const logout = createAsyncThunk<void, void, { rejectValue: string }>(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      localStorage.removeItem('token');
    } catch (error: any) {
      return rejectWithValue('Failed to logout');
    }
  }
);

// Fetch user profile
export const fetchUserProfile = createAsyncThunk<
  User,
  void,
  { rejectValue: string }
>(
  'auth/fetchUserProfile',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue('No token found');
      }
      
      const response = await axios.get<User>(
        `${process.env.REACT_APP_API_URL}/api/v1/users/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      
      return response.data;
    } catch (error: any) {
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
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
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
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string || 'Registration failed';
      })
      
      // Handle logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      
      // Handle fetch user profile
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(fetchUserProfile.rejected, (state) => {
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        localStorage.removeItem('token');
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;