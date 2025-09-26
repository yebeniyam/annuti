import React, { useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';


// Types for POS system
interface TableInfo {
  id: string;
  name: string;
  capacity: number;
  status: 'available' | 'occupied' | 'reserved' | 'dirty';
  section_id: string;
}

interface Order {
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

interface OrderItem {
  id: string;
  order_id: string;
  menu_item_id: string;
  menu_item_name: string;
  quantity: number;
  unit_price: number;
  notes?: string;
  status: 'new' | 'preparing' | 'ready' | 'served';
}

const POS: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedTable, setSelectedTable] = useState<TableInfo | null>(null);
  
  const [openPaymentDialog, setOpenPaymentDialog] = useState(false);
  
  const error = null; // Placeholder

  // Sample data - would normally come from state
  const [tables] = useState<TableInfo[]>([
    { id: '1', name: 'Table 1', capacity: 4, status: 'available', section_id: 'A' },
    { id: '2', name: 'Table 2', capacity: 4, status: 'occupied', section_id: 'A' },
    { id: '3', name: 'Table 3', capacity: 6, status: 'available', section_id: 'A' },
    { id: '4', name: 'Table 4', capacity: 2, status: 'dirty', section_id: 'B' },
    { id: '5', name: 'Table 5', capacity: 2, status: 'occupied', section_id: 'B' },
    { id: '6', name: 'Bar Seat 1', capacity: 1, status: 'available', section_id: 'C' },
    { id: '7', name: 'Bar Seat 2', capacity: 1, status: 'available', section_id: 'C' },
  ]);

  const [menuItems] = useState([
    { id: '1', name: 'Beef Burger', price: 250, category: 'Burgers' },
    { id: '2', name: 'Chicken Burger', price: 220, category: 'Burgers' },
    { id: '3', name: 'Coke 330ml', price: 40, category: 'Drinks' },
    { id: '4', name: 'Fanta 330ml', price: 40, category: 'Drinks' },
    { id: '5', name: 'French Fries', price: 80, category: 'Sides' },
    { id: '6', name: 'Onion Rings', price: 90, category: 'Sides' },
  ]);

  const [currentOrder, setCurrentOrder] = useState<Order | null>(null);
  const [orderItems, setOrderItems] = useState<OrderItem[]>([]);
  const [newOrderItem, setNewOrderItem] = useState({
    menu_item_id: '',
    quantity: 1,
    notes: '',
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleTableSelect = (table: TableInfo) => {
    setSelectedTable(table);
    // In a real app, this would fetch the existing order for the table
    setCurrentOrder(null);
    setOrderItems([]);
    
  };

  const handleAddItem = () => {
    if (!newOrderItem.menu_item_id) return;
    
    const menuItem = menuItems.find(item => item.id === newOrderItem.menu_item_id);
    if (!menuItem) return;
    
    const newItem: OrderItem = {
      id: Date.now().toString(),
      order_id: currentOrder?.id || 'new',
      menu_item_id: newOrderItem.menu_item_id,
      menu_item_name: menuItem.name,
      quantity: newOrderItem.quantity,
      unit_price: menuItem.price,
      notes: newOrderItem.notes,
      status: 'new',
    };
    
    setOrderItems([...orderItems, newItem]);
    
    // Reset form
    setNewOrderItem({
      menu_item_id: '',
      quantity: 1,
      notes: '',
    });
  };

  const handleRemoveItem = (itemId: string) => {
    setOrderItems(orderItems.filter(item => item.id !== itemId));
  };

  const calculateTotals = () => {
    const subtotal = orderItems.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
    const tax = subtotal * 0.15; // 15% tax
    const total = subtotal + tax;
    
    return { subtotal, tax, total };
  };

  const { subtotal, tax, total } = calculateTotals();

  const handleOpenPayment = () => {
    setOpenPaymentDialog(true);
  };

  const handlePayment = () => {
    // In a real app, this would process the payment
    console.log('Processing payment...');
    setOpenPaymentDialog(false);
  };

  const getStatusColor = (status: TableInfo['status']) => {
    switch (status) {
      case 'available': return '#4caf50'; // Green
      case 'occupied': return '#ff9800'; // Orange
      case 'reserved': return '#2196f3'; // Blue
      case 'dirty': return '#9e9e9e'; // Gray
      default: return '#9e9e9e'; // Gray
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Point of Sale (POS)
      </Typography>

      {error && <div>{error}</div>}

      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Floor Plan" />
            <Tab label="Current Order" />
            <Tab label="Kitchen Display" />
          </Tabs>
        </Box>

        {/* Floor Plan Tab */}
        {activeTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Restaurant Floor Plan
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                <Box 
                  sx={{ 
                    border: '1px solid #ccc', 
                    p: 3, 
                    borderRadius: 2,
                    minHeight: 400,
                    backgroundColor: '#f9f9f9'
                  }}
                >
                  <Grid container spacing={2}>
                    {tables.map((table) => (
                      <Grid item xs={2} key={table.id}>
                        <Card
                          sx={{
                            backgroundColor: getStatusColor(table.status),
                            cursor: 'pointer',
                            '&:hover': {
                              opacity: 0.8,
                            },
                          }}
                          onClick={() => handleTableSelect(table)}
                        >
                          <CardContent sx={{ textAlign: 'center', padding: 1 }}>
                            <Typography variant="h6" color="white">
                              {table.name}
                            </Typography>
                            <Typography variant="body2" color="white">
                              {table.capacity} {table.capacity === 1 ? 'person' : 'people'}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Table Status Legend
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText 
                        primary={
                          <Box display="flex" alignItems="center">
                            <Box 
                              sx={{ 
                                width: 16, 
                                height: 16, 
                                backgroundColor: '#4caf50', 
                                borderRadius: '50%',
                                mr: 1
                              }} 
                            />
                            Available
                          </Box>
                        } 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary={
                          <Box display="flex" alignItems="center">
                            <Box 
                              sx={{ 
                                width: 16, 
                                height: 16, 
                                backgroundColor: '#ff9800', 
                                borderRadius: '50%',
                                mr: 1
                              }} 
                            />
                            Occupied
                          </Box>
                        } 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary={
                          <Box display="flex" alignItems="center">
                            <Box 
                              sx={{ 
                                width: 16, 
                                height: 16, 
                                backgroundColor: '#2196f3', 
                                borderRadius: '50%',
                                mr: 1
                              }} 
                            />
                            Reserved
                          </Box>
                        } 
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText 
                        primary={
                          <Box display="flex" alignItems="center">
                            <Box 
                              sx={{ 
                                width: 16, 
                                height: 16, 
                                backgroundColor: '#9e9e9e', 
                                borderRadius: '50%',
                                mr: 1
                              }} 
                            />
                            Dirty
                          </Box>
                        } 
                      />
                    </ListItem>
                  </List>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Current Order Tab */}
        {activeTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Current Order
            </Typography>
            
            {selectedTable ? (
              <Box>
                <Typography variant="h5" gutterBottom>
                  Table: {selectedTable.name} - {selectedTable.capacity} seats
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                  <Box flex={1}>
                    <Typography variant="h6" gutterBottom>Menu</Typography>
                    <Grid container spacing={2}>
                      {menuItems.map((item) => (
                        <Grid item xs={6} sm={4} md={3} key={item.id}>
                          <Card>
                            <CardContent>
                              <Typography variant="subtitle1">{item.name}</Typography>
                              <Typography variant="body2" color="textSecondary">
                                {item.category}
                              </Typography>
                              <Typography variant="h6" color="primary">
                                {item.price} Birr
                              </Typography>
                            </CardContent>
                            <CardActions>
                              <Button 
                                size="small" 
                                onClick={() => {
                                  setNewOrderItem({
                                    ...newOrderItem,
                                    menu_item_id: item.id
                                  });
                                  handleAddItem();
                                }}
                              >
                                Add
                              </Button>
                            </CardActions>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                  
                  <Box flex={1}>
                    <Typography variant="h6" gutterBottom>Order Items</Typography>
                    
                    <List>
                      {orderItems.map((item) => (
                        <ListItem key={item.id} sx={{ border: '1px solid #eee', mb: 1 }}>
                          <ListItemText
                            primary={`${item.quantity}x ${item.menu_item_name}`}
                            secondary={`Price: ${item.unit_price} Birr each`}
                          />
                          <ListItemText 
                            primary={`${item.unit_price * item.quantity} Birr`} 
                            sx={{ textAlign: 'right' }}
                          />
                          <Button 
                            size="small" 
                            color="error" 
                            onClick={() => handleRemoveItem(item.id)}
                          >
                            Remove
                          </Button>
                        </ListItem>
                      ))}
                    </List>
                    
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="h6">Add Item</Typography>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 2 }}>
                        <FormControl fullWidth margin="dense">
                          <InputLabel>Menu Item</InputLabel>
                          <Select
                            value={newOrderItem.menu_item_id}
                            label="Menu Item"
                            onChange={(e) => setNewOrderItem({...newOrderItem, menu_item_id: e.target.value})}
                          >
                            {menuItems.map((item) => (
                              <MenuItem key={item.id} value={item.id}>
                                {item.name} - {item.price} Birr
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                        
                        <TextField
                          label="Quantity"
                          type="number"
                          value={newOrderItem.quantity}
                          onChange={(e) => setNewOrderItem({...newOrderItem, quantity: parseInt(e.target.value) || 1})}
                          inputProps={{ min: 1 }}
                          sx={{ width: 100 }}
                        />
                        
                        <Button variant="contained" color="primary" onClick={handleAddItem}>
                          Add
                        </Button>
                      </Box>
                    </Box>
                    
                    <Divider sx={{ my: 2 }} />
                    
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography variant="h6">Subtotal: {subtotal.toFixed(2)} Birr</Typography>
                      <Typography variant="h6">Tax: {tax.toFixed(2)} Birr</Typography>
                      <Typography variant="h5" color="primary">
                        Total: {total.toFixed(2)} Birr
                      </Typography>
                      
                      <Box sx={{ mt: 2 }}>
                        <Button 
                          variant="contained" 
                          color="primary" 
                          size="large"
                          onClick={handleOpenPayment}
                          disabled={orderItems.length === 0}
                        >
                          Process Payment
                        </Button>
                      </Box>
                    </Box>
                  </Box>
                </Box>
              </Box>
            ) : (
              <Typography variant="body1" color="textSecondary">
                Select a table from the floor plan to start an order.
              </Typography>
            )}
          </Box>
        )}

        {/* Kitchen Display Tab */}
        {activeTab === 2 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Kitchen Display
            </Typography>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Order ID</TableCell>
                    <TableCell>Table</TableCell>
                    <TableCell>Items</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Time</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {/* In a real app, this would show orders in progress */}
                  <TableRow>
                    <TableCell>ORD001</TableCell>
                    <TableCell>Table 2</TableCell>
                    <TableCell>
                      <List dense>
                        <ListItem><ListItemText primary="2x Beef Burger" /></ListItem>
                        <ListItem><ListItemText primary="1x French Fries" /></ListItem>
                      </List>
                    </TableCell>
                    <TableCell>
                      <Chip label="Preparing" color="warning" />
                    </TableCell>
                    <TableCell>10:30 AM</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>ORD002</TableCell>
                    <TableCell>Table 5</TableCell>
                    <TableCell>
                      <List dense>
                        <ListItem><ListItemText primary="1x Chicken Burger" /></ListItem>
                        <ListItem><ListItemText primary="2x Coke 330ml" /></ListItem>
                      </List>
                    </TableCell>
                    <TableCell>
                      <Chip label="Ready" color="success" />
                    </TableCell>
                    <TableCell>10:45 AM</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Paper>

      {/* Payment Dialog */}
      <Dialog open={openPaymentDialog} onClose={() => setOpenPaymentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Process Payment</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" gutterBottom>Payment Details</Typography>
            <Typography>Subtotal: {subtotal.toFixed(2)} Birr</Typography>
            <Typography>Tax: {tax.toFixed(2)} Birr</Typography>
            <Typography variant="h5" color="primary">Total: {total.toFixed(2)} Birr</Typography>
            
            <Box sx={{ mt: 2 }}>
              <FormControl fullWidth margin="dense">
                <InputLabel>Payment Method</InputLabel>
                <Select label="Payment Method">
                  <MenuItem value="cash">Cash</MenuItem>
                  <MenuItem value="card">Card</MenuItem>
                  <MenuItem value="telebirr">TeleBirr</MenuItem>
                  <MenuItem value="chapa">Chapa</MenuItem>
                </Select>
              </FormControl>
              
              <TextField
                label="Amount Received"
                type="number"
                fullWidth
                margin="dense"
                placeholder="Enter amount received"
              />
              
              <Typography sx={{ mt: 2 }}>Change: 0.00 Birr</Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenPaymentDialog(false)}>Cancel</Button>
          <Button onClick={handlePayment} variant="contained" color="primary">Process Payment</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default POS;