// Menu-related types

export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  cost: number; // COGS
  category_id: string;
  category_name: string;
  is_available: boolean;
  image_url?: string;
  prep_time?: number;
  is_featured?: boolean;
}

export interface MenuCategory {
  id: string;
  name: string;
  description: string;
  display_order: number;
  is_active: boolean;
}

export interface Recipe {
  id: string;
  menu_item_id: string;
  instructions: string;
  yield_count: number;
  yield_unit: string;
}

export interface RecipeIngredient {
  id: string;
  recipe_id: string;
  ingredient_id: string;
  quantity: number;
  unit: string;
  notes?: string;
}