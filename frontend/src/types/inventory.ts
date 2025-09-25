// Inventory-related types

export interface InventoryItem {
  id: string;
  name: string;
  category: string;
  current_stock: number;
  unit: string;
  unit_cost: number;
  min_stock: number;
  supplier: string;
  category_type: string;
}

export interface InventoryTransaction {
  id: string;
  type: 'receiving' | 'issuing' | 'adjustment';
  reference_id: string;
  date: string;
  notes: string;
  user_id: string;
}

export interface Unit {
  id: string;
  name: string;
  abbreviation: string;
  base_unit_id?: string;
  conversion_factor?: number;
}

export interface InventoryCount {
  id: string;
  date: string;
  status: 'draft' | 'in-progress' | 'completed';
  notes: string;
  user_id: string;
}

export interface InventoryCountItem {
  id: string;
  count_id: string;
  ingredient_id: string;
  counted_quantity: number;
  system_quantity: number;
  variance: number;
  notes?: string;
}