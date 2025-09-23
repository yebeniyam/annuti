# Bendine Food and Beverage Management System - Project Plan

## Project Overview
Bendine is a comprehensive Food and Beverage Management System designed to streamline restaurant operations, from menu management to point of sale, inventory, and reporting.

## Technical Stack
- **Frontend**: React (Hosted on cPanel)
- **Backend**: Python FastAPI (Hosted on Render)
- **Database/Auth/Realtime/Storage**: Supabase
- **Mobile**: React Native (for Waiter App)

## Development Phases

### Phase 1: Project Setup & Core Infrastructure (Week 1-2)
- [ ] **Project Initialization**
  - Set up Git repository
  - Create project structure
  - Configure development environment
- [ ] **Frontend Setup**
  - Initialize React application with TypeScript
  - Set up routing (React Router)
  - Configure state management (Redux/Context API)
  - Set up UI component library (e.g., Material-UI or Chakra UI)
- [ ] **Backend Setup**
  - Set up FastAPI project
  - Configure database connection (Supabase)
  - Implement basic API structure
  - Set up CORS and middleware
- [ ] **Supabase Configuration**
  - Create project
  - Set up authentication
  - Design initial database schema
  - Configure storage buckets

### Phase 2: Core Features Development (Week 3-8)

#### Module 1: Authentication & User Management (Week 3)
- [ ] User authentication (login/logout)
- [ ] Role-based access control
- [ ] User management interface
- [ ] Profile management

#### Module 2: Menu Management (Week 4)
- [ ] CRUD operations for menu items
- [ ] Menu categories and organization
- [ ] Recipe builder with COGS calculation
- [ ] Menu item images and details

#### Module 3: Inventory Management (Week 5-6)
- [ ] Inventory item management
- [ ] Receiving and issuing stock
- [ ] Inventory counting and variance reporting
- [ ] Low stock alerts

#### Module 4: POS System (Week 7-8)
- [ ] Table management
- [ ] Order creation and modification
- [ ] Payment processing
- [ ] Real-time order status

### Phase 3: Advanced Features (Week 9-12)

#### Module 5: Reporting & Analytics (Week 9)
- [ ] Sales reports
- [ ] Inventory valuation
- [ ] COGS analysis
- [ ] Staff performance metrics

#### Module 6: Vendor & Purchase Management (Week 10)
- [ ] Vendor management
- [ ] Purchase order system
- [ ] Vendor performance tracking

#### Module 7: Mobile Waiter App (Week 11-12)
- [ ] React Native setup
- [ ] Authentication
- [ ] Table and order management
- [ ] Real-time updates

### Phase 4: Integration & Testing (Week 13-14)
- [ ] System integration
- [ ] Unit and integration testing
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Security testing

### Phase 5: Deployment (Week 15)
- [ ] Backend deployment to Render
- [ ] Frontend deployment to cPanel
- [ ] Mobile app deployment to app stores
- [ ] CI/CD pipeline setup

### Phase 6: Documentation & Training (Week 16)
- [ ] API documentation
- [ ] User manuals
- [ ] Training materials
- [ ] Handover documentation

## Technical Specifications

### Complete Database Schema

#### 1. Authentication & Users
- `users` - User accounts and authentication
  - id, email, password_hash, full_name, role, phone, created_at, updated_at, last_login
- `roles` - User roles and permissions
  - id, name, description, permissions
- `sessions` - User login sessions
  - id, user_id, token, expires_at, created_at

#### 2. Menu Management
- `menu_categories` - Menu categories
  - id, name, description, display_order, is_active
- `menu_items` - Menu items
  - id, category_id, name, description, price, cost, is_available, image_url, prep_time, is_featured
- `ingredients` - Raw ingredients
  - id, name, description, unit, current_stock, min_stock, unit_cost, supplier_id, category
- `recipes` - Menu item recipes
  - id, menu_item_id, instructions, yield_count, yield_unit
- `recipe_ingredients` - Ingredients for each recipe
  - id, recipe_id, ingredient_id, quantity, unit, notes
- `modifiers` - Item modifiers (e.g., no onions, extra cheese)
  - id, name, description, price_adjustment
- `menu_item_modifiers` - Link between menu items and modifiers
  - id, menu_item_id, modifier_id, is_required

#### 3. Inventory Management
- `inventory_items` - Current inventory
  - id, ingredient_id, quantity, unit, location, expiry_date, batch_number
- `inventory_transactions` - All stock movements
  - id, type (receiving/issuing/adjustment), reference_id, date, notes, user_id
- `inventory_transaction_items` - Items in each transaction
  - id, transaction_id, ingredient_id, quantity, unit_cost, total_cost, expiry_date, batch_number
- `inventory_counts` - Physical inventory counts
  - id, date, status, notes, user_id
- `inventory_count_items` - Items in each count
  - id, count_id, ingredient_id, counted_quantity, system_quantity, variance, notes
- `units` - Measurement units
  - id, name, abbreviation, base_unit_id, conversion_factor
- `unit_conversions` - Unit conversions
  - id, from_unit_id, to_unit_id, conversion_factor

#### 4. POS & Orders
- `tables` - Restaurant tables
  - id, name, capacity, status (available/occupied/reserved), section_id
- `table_sections` - Restaurant sections
  - id, name, description
- `reservations` - Table reservations
  - id, table_id, customer_name, customer_phone, party_size, reservation_time, status, notes
- `orders` - Customer orders
  - id, table_id, status, customer_name, customer_phone, party_size, order_type (dine-in/takeout/delivery), subtotal, tax, discount, total, payment_status, created_at, updated_at, user_id
- `order_items` - Items in each order
  - id, order_id, menu_item_id, quantity, unit_price, notes, status, kitchen_notes
- `order_item_modifiers` - Modifiers for order items
  - id, order_item_id, modifier_id, name, price_adjustment
- `order_status_history` - Order status changes
  - id, order_id, status, notes, created_at, user_id

#### 5. Payments & Billing
- `payments` - Payment transactions
  - id, order_id, amount, payment_method, transaction_id, status, notes, created_at, user_id
- `payment_methods` - Available payment methods
  - id, name, is_active, requires_processing
- `invoices` - Customer invoices
  - id, order_id, invoice_number, issue_date, due_date, status, subtotal, tax, discount, total, notes
- `discounts` - Discount configurations
  - id, name, description, type (percentage/fixed), value, is_active, valid_from, valid_until

#### 6. Vendor & Purchasing
- `vendors` - Suppliers/vendors
  - id, name, contact_person, email, phone, address, tax_id, payment_terms, notes
- `purchase_orders` - Purchase orders
  - id, vendor_id, order_date, expected_delivery_date, status, subtotal, tax, total, notes, created_by, approved_by, approved_at
- `purchase_order_items` - Items in purchase orders
  - id, po_id, ingredient_id, quantity, unit, unit_cost, total_cost, received_quantity
- `receivings` - Received inventory
  - id, po_id, receiving_date, received_by, notes, invoice_number, invoice_date
- `receiving_items` - Items in each receiving
  - id, receiving_id, po_item_id, ingredient_id, quantity, unit_cost, expiry_date, batch_number

#### 7. Reporting
- `sales_summaries` - Daily sales summaries
  - id, date, total_sales, total_tax, total_discount, total_net, total_orders, avg_order_value
- `inventory_valuation` - Inventory value over time
  - id, date, total_value, item_count
- `waste_logs` - Recorded waste
  - id, ingredient_id, quantity, unit, reason, cost, date, recorded_by, notes

### Complete API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user (admin only)
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update current user profile
- `PUT /api/auth/change-password` - Change password
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token

#### Users & Roles
- `GET /api/users` - List all users (admin only)
- `POST /api/users` - Create new user (admin only)
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user (admin only)
- `GET /api/roles` - List all roles
- `POST /api/roles` - Create new role (admin only)
- `GET /api/roles/{id}` - Get role by ID
- `PUT /api/roles/{id}` - Update role (admin only)
- `DELETE /api/roles/{id}` - Delete role (admin only)

#### Menu Management
- `GET /api/menu/categories` - List all categories
- `POST /api/menu/categories` - Create category
- `GET /api/menu/categories/{id}` - Get category by ID
- `PUT /api/menu/categories/{id}` - Update category
- `DELETE /api/menu/categories/{id}` - Delete category
- `GET /api/menu/items` - List all menu items
- `POST /api/menu/items` - Create menu item
- `GET /api/menu/items/{id}` - Get menu item by ID
- `PUT /api/menu/items/{id}` - Update menu item
- `DELETE /api/menu/items/{id}` - Delete menu item
- `GET /api/menu/items/{id}/recipe` - Get item recipe
- `PUT /api/menu/items/{id}/recipe` - Update item recipe
- `GET /api/ingredients` - List all ingredients
- `POST /api/ingredients` - Create ingredient
- `GET /api/ingredients/{id}` - Get ingredient by ID
- `PUT /api/ingredients/{id}` - Update ingredient
- `DELETE /api/ingredients/{id}` - Delete ingredient
- `GET /api/modifiers` - List all modifiers
- `POST /api/modifiers` - Create modifier
- `GET /api/modifiers/{id}` - Get modifier by ID
- `PUT /api/modifiers/{id}` - Update modifier
- `DELETE /api/modifiers/{id}` - Delete modifier

#### Inventory Management
- `GET /api/inventory` - List all inventory items
- `GET /api/inventory/transactions` - List inventory transactions
- `POST /api/inventory/transactions` - Create inventory transaction
- `GET /api/inventory/transactions/{id}` - Get transaction by ID
- `GET /api/inventory/transactions/types` - List transaction types
- `GET /api/inventory/counts` - List inventory counts
- `POST /api/inventory/counts` - Create inventory count
- `GET /api/inventory/counts/{id}` - Get count by ID
- `POST /api/inventory/counts/{id}/complete` - Complete inventory count
- `GET /api/inventory/low-stock` - Get low stock items
- `GET /api/units` - List all units
- `POST /api/units` - Create unit
- `GET /api/units/{id}` - Get unit by ID
- `PUT /api/units/{id}` - Update unit
- `DELETE /api/units/{id}` - Delete unit
- `GET /api/unit-conversions` - List all unit conversions
- `POST /api/unit-conversions` - Create unit conversion
- `DELETE /api/unit-conversions/{id}` - Delete unit conversion

#### POS & Orders
- `GET /api/tables` - List all tables
- `POST /api/tables` - Create table
- `GET /api/tables/{id}` - Get table by ID
- `PUT /api/tables/{id}` - Update table
- `DELETE /api/tables/{id}` - Delete table
- `GET /api/table-sections` - List table sections
- `POST /api/table-sections` - Create table section
- `GET /api/table-sections/{id}` - Get section by ID
- `PUT /api/table-sections/{id}` - Update section
- `DELETE /api/table-sections/{id}` - Delete section
- `GET /api/reservations` - List reservations
- `POST /api/reservations` - Create reservation
- `GET /api/reservations/{id}` - Get reservation by ID
- `PUT /api/reservations/{id}` - Update reservation
- `DELETE /api/reservations/{id}` - Delete reservation
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order
- `GET /api/orders/{id}` - Get order by ID
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order
- `POST /api/orders/{id}/status` - Update order status
- `GET /api/orders/{id}/items` - Get order items
- `POST /api/orders/{id}/items` - Add item to order
- `PUT /api/orders/{orderId}/items/{itemId}` - Update order item
- `DELETE /api/orders/{orderId}/items/{itemId}` - Remove item from order

#### Payments & Billing
- `GET /api/payments` - List payments
- `POST /api/payments` - Process payment
- `GET /api/payments/{id}` - Get payment by ID
- `GET /api/payment-methods` - List payment methods
- `POST /api/payment-methods` - Create payment method (admin only)
- `PUT /api/payment-methods/{id}` - Update payment method (admin only)
- `DELETE /api/payment-methods/{id}` - Delete payment method (admin only)
- `GET /api/invoices` - List invoices
- `GET /api/invoices/{id}` - Get invoice by ID
- `POST /api/invoices/{id}/send` - Send invoice to customer
- `GET /api/discounts` - List discounts
- `POST /api/discounts` - Create discount (admin only)
- `PUT /api/discounts/{id}` - Update discount (admin only)
- `DELETE /api/discounts/{id}` - Delete discount (admin only)

#### Vendor & Purchasing
- `GET /api/vendors` - List vendors
- `POST /api/vendors` - Create vendor
- `GET /api/vendors/{id}` - Get vendor by ID
- `PUT /api/vendors/{id}` - Update vendor
- `DELETE /api/vendors/{id}` - Delete vendor
- `GET /api/purchase-orders` - List purchase orders
- `POST /api/purchase-orders` - Create purchase order
- `GET /api/purchase-orders/{id}` - Get purchase order by ID
- `PUT /api/purchase-orders/{id}` - Update purchase order
- `DELETE /api/purchase-orders/{id}` - Delete purchase order
- `POST /api/purchase-orders/{id}/approve` - Approve purchase order
- `POST /api/purchase-orders/{id}/receive` - Receive items from purchase order
- `GET /api/receivings` - List receivings
- `GET /api/receivings/{id}` - Get receiving by ID

#### Reporting
- `GET /api/reports/sales` - Sales report
- `GET /api/reports/inventory` - Inventory valuation report
- `GET /api/reports/profitability` - Menu item profitability report
- `GET /api/reports/variance` - Inventory variance report
- `GET /api/reports/employee` - Employee performance report
- `GET /api/reports/customer` - Customer spending report
- `GET /api/dashboard/summary` - Dashboard summary
- `GET /api/dashboard/sales-trend` - Sales trend data
- `GET /api/dashboard/top-items` - Top selling items
- `GET /api/dashboard/low-stock` - Low stock alerts

## Risk Management

### Technical Risks
1. **Real-time Updates**
   - Mitigation: Use Supabase Realtime for efficient updates

2. **Data Consistency**
   - Mitigation: Implement transactions for critical operations

3. **Performance**
   - Mitigation: Optimize queries and implement caching

### Project Risks
1. **Timeline**
   - Mitigation: Regular progress reviews and scope management

2. **Resource Constraints**
   - Mitigation: Prioritize features based on business value

## Success Metrics
1. System performance (response time < 500ms)
2. User adoption rate (>80% of staff)
3. Reduction in order processing time (>30%)
4. Decrease in inventory variance (<2%)

## Next Steps
1. Set up development environment
2. Create initial database schema
3. Implement authentication system
4. Develop core menu management features

## Team & Responsibilities
- **Project Manager**: Overall project coordination
- **Frontend Developer**: React application development
- **Backend Developer**: FastAPI development
- **Mobile Developer**: React Native app development
- **QA Engineer**: Testing and quality assurance

## Timeline
- **Total Duration**: 16 weeks
- **Start Date**: [To be determined]
- **Expected Completion**: [To be determined]

## Budget
- Development: $XX,XXX
- Hosting & Services: $XXX/month
- Maintenance: $XXX/month (post-launch)
