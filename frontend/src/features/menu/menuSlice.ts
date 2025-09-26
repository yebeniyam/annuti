import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { MenuItem, MenuCategory } from '../../types/menu';

interface MenuState {
  categories: MenuCategory[];
  items: MenuItem[];
  loading: boolean;
  error: string | null;
}

// Async thunk for fetching menu categories
export const fetchCategories = createAsyncThunk(
  'menu/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No token found');
      }

      const response = await axios.get<MenuCategory[]>(
        `${process.env.REACT_APP_API_URL}/api/v1/menu/categories`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to fetch categories'
      );
    }
  }
);

// Async thunk for fetching menu items
export const fetchMenuItems = createAsyncThunk(
  'menu/fetchItems',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No token found');
      }

      const response = await axios.get<MenuItem[]>(
        `${process.env.REACT_APP_API_URL}/api/v1/menu/items`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to fetch menu items'
      );
    }
  }
);

// Async thunk for adding a menu item
export const addMenuItem = createAsyncThunk(
  'menu/addItem',
  async (itemData: Omit<MenuItem, 'id'>, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No token found');
      }

      const response = await axios.post<MenuItem>(
        `${process.env.REACT_APP_API_URL}/api/v1/menu/items`,
        itemData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to add menu item'
      );
    }
  }
);

// Async thunk for updating a menu item
export const updateMenuItem = createAsyncThunk(
  'menu/updateItem',
  async ({ id, itemData }: { id: string; itemData: Partial<MenuItem> }, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No token found');
      }

      const response = await axios.put<MenuItem>(
        `${process.env.REACT_APP_API_URL}/api/v1/menu/items/${id}`,
        itemData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to update menu item'
      );
    }
  }
);

// Async thunk for deleting a menu item
export const deleteMenuItem = createAsyncThunk(
  'menu/deleteItem',
  async (itemId: string, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No token found');
      }

      await axios.delete(
        `${process.env.REACT_APP_API_URL}/api/v1/menu/items/${itemId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return itemId;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to delete menu item'
      );
    }
  }
);

const initialState: MenuState = {
  categories: [],
  items: [],
  loading: false,
  error: null,
};

const menuSlice = createSlice({
  name: 'menu',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch categories cases
      .addCase(fetchCategories.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCategories.fulfilled, (state, action: PayloadAction<MenuCategory[]>) => {
        state.loading = false;
        state.categories = action.payload;
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Fetch menu items cases
      .addCase(fetchMenuItems.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMenuItems.fulfilled, (state, action: PayloadAction<MenuItem[]>) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchMenuItems.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // Add menu item cases
      .addCase(addMenuItem.fulfilled, (state, action: PayloadAction<MenuItem>) => {
        state.items.push(action.payload);
      })
      .addCase(addMenuItem.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      // Update menu item cases
      .addCase(updateMenuItem.fulfilled, (state, action: PayloadAction<MenuItem>) => {
        const index = state.items.findIndex(item => item.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      })
      .addCase(updateMenuItem.rejected, (state, action) => {
        state.error = action.payload as string;
      })
      // Delete menu item cases
      .addCase(deleteMenuItem.fulfilled, (state, action: PayloadAction<string>) => {
        state.items = state.items.filter(item => item.id !== action.payload);
      })
      .addCase(deleteMenuItem.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

export const { clearError } = menuSlice.actions;
export default menuSlice.reducer;