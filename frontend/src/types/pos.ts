// POS-related types

export interface Table {
  id: string;
  name: string;
  capacity: number;
  status: 'available' | 'occupied' | 'reserved' | 'dirty';
  section_id: string;
}

export interface Order {
  id: string;
  table_id: string;
  status: 'new' | 'preparing' | 'ready' | 'served' | 'paid';
  customer_name?: string;
  customer_phone?: string;
  party_size?: number;
  order_type: 'dine-in' | 'takeout' | 'delivery';
  subtotal: number;
  tax: number;
  discount: number;
  total: number;
  payment_status: 'pending' | 'partial' | 'paid';
  created_at: string;
  updated_at: string;
  user_id: string;
}

export interface OrderItem {
  id: string;
  order_id: string;
  menu_item_id: string;
  menu_item_name: string;
  quantity: number;
  unit_price: number;
  notes?: string;
  status: 'new' | 'preparing' | 'ready' | 'served';
}

export interface Payment {
  id: string;
  order_id: string;
  amount: number;
  payment_method: 'cash' | 'card' | 'telebirr' | 'chapa';
  transaction_id?: string;
  status: 'pending' | 'completed' | 'failed';
  notes?: string;
  created_at: string;
  user_id: string;
}