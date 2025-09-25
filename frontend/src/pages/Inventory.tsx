import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Box,
  Tabs,
  Tab,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
} from '@mui/material';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';

// Define types for inventory
interface InventoryItem {
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

interface InventoryTransaction {
  id: string;
  type: 'receiving' | 'issuing' | 'adjustment';
  reference_id: string;
  date: string;
  notes: string;
  user_id: string;
}

interface Unit {
  id: string;
  name: string;
  abbreviation: string;
}

const Inventory: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<'add' | 'edit'>('add');
  const [currentItem, setCurrentItem] = useState<InventoryItem | null>(null);
  
  // Form state
  const [name, setName] = useState('');
  const [category, setCategory] = useState('');
  const [currentStock, setCurrentStock] = useState('');
  const [unit, setUnit] = useState('');
  const [unitCost, setUnitCost] = useState('');
  const [minStock, setMinStock] = useState('');
  const [supplier, setSupplier] = useState('');
  const [categoryType, setCategoryType] = useState('');
  
  const dispatch = useDispatch<AppDispatch>();
  const { loading, error } = useSelector((state: RootState) => ({
    loading: false, // Placeholder - would be from actual inventory state
    error: null, // Placeholder - would be from actual inventory state
  }));

  // Sample inventory items - these would normally come from state
  const [inventoryItems] = useState<InventoryItem[]>([
    { 
      id: '1', 
      name: 'Beef', 
      category: 'Raw Materials',
      current_stock: 12.5,
      unit: 'kg',
      unit_cost: 620,
      min_stock: 5,
      supplier: 'Fresh Meat Co.',
      category_type: 'Meat'
    },
    { 
      id: '2', 
      name: 'Buns', 
      category: 'Raw Materials',
      current_stock: 240,
      unit: 'pcs',
      unit_cost: 5.2,
      min_stock: 100,
      supplier: 'Bun Supply Ltd.',
      category_type: 'Bakery'
    },
    { 
      id: '3', 
      name: 'Lettuce', 
      category: 'Raw Materials',
      current_stock: 15.2,
      unit: 'kg',
      unit_cost: 80,
      min_stock: 3,
      supplier: 'Fresh Vegetables Inc.',
      category_type: 'Vegetables'
    },
  ]);

  // Sample units
  const [units] = useState<Unit[]>([
    { id: '1', name: 'kilogram', abbreviation: 'kg' },
    { id: '2', name: 'gram', abbreviation: 'g' },
    { id: '3', name: 'piece', abbreviation: 'pcs' },
    { id: '4', name: 'liter', abbreviation: 'L' },
    { id: '5', name: 'milliliter', abbreviation: 'ml' },
  ]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleOpenDialog = (mode: 'add' | 'edit', item?: InventoryItem) => {
    setDialogMode(mode);
    
    if (mode === 'edit' && item) {
      setCurrentItem(item);
      setName(item.name);
      setCategory(item.category);
      setCurrentStock(item.current_stock.toString());
      setUnit(item.unit);
      setUnitCost(item.unit_cost.toString());
      setMinStock(item.min_stock.toString());
      setSupplier(item.supplier);
      setCategoryType(item.category_type);
    } else {
      // Reset form for adding new item
      setCurrentItem(null);
      setName('');
      setCategory('');
      setCurrentStock('');
      setUnit('');
      setUnitCost('');
      setMinStock('');
      setSupplier('');
      setCategoryType('');
    }
    
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // In a real app, this would dispatch an action to add/update item
    console.log({
      name,
      category,
      current_stock: parseFloat(currentStock),
      unit,
      unit_cost: parseFloat(unitCost),
      min_stock: parseFloat(minStock),
      supplier,
      category_type: categoryType
    });
    
    handleCloseDialog();
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Inventory Management
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Inventory Items" />
            <Tab label="Transactions" />
            <Tab label="Units" />
            <Tab label="Low Stock" />
          </Tabs>
        </Box>

        {/* Inventory Items Tab */}
        {activeTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Inventory Items</Typography>
              <Box>
                <Button 
                  variant="outlined" 
                  color="secondary" 
                  sx={{ mr: 1 }}
                >
                  Receive
                </Button>
                <Button 
                  variant="outlined" 
                  color="secondary" 
                  sx={{ mr: 1 }}
                >
                  Issue
                </Button>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={() => handleOpenDialog('add')}
                >
                  Add Item
                </Button>
              </Box>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Current Stock</TableCell>
                    <TableCell>Unit</TableCell>
                    <TableCell>Unit Cost (Birr)</TableCell>
                    <TableCell>Total Value (Birr)</TableCell>
                    <TableCell>Min Stock</TableCell>
                    <TableCell>Supplier</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {inventoryItems.map((item) => (
                    <TableRow 
                      key={item.id} 
                      sx={{ 
                        backgroundColor: item.current_stock <= item.min_stock ? '#ffebee' : 'inherit' // Red background for low stock
                      }}
                    >
                      <TableCell>{item.id}</TableCell>
                      <TableCell>{item.name}</TableCell>
                      <TableCell>{item.category}</TableCell>
                      <TableCell>{item.current_stock} {item.unit}</TableCell>
                      <TableCell>{item.unit}</TableCell>
                      <TableCell>{item.unit_cost.toFixed(2)}</TableCell>
                      <TableCell>{(item.current_stock * item.unit_cost).toFixed(2)}</TableCell>
                      <TableCell>{item.min_stock} {item.unit}</TableCell>
                      <TableCell>{item.supplier}</TableCell>
                      <TableCell>
                        {item.current_stock <= item.min_stock ? (
                          <span style={{ color: 'red' }}>Low Stock!</span>
                        ) : item.current_stock <= (item.min_stock * 1.5) ? (
                          <span style={{ color: 'orange' }}>Warning</span>
                        ) : (
                          <span style={{ color: 'green' }}>OK</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button 
                          size="small" 
                          variant="outlined" 
                          sx={{ mr: 1 }}
                          onClick={() => handleOpenDialog('edit', item)}
                        >
                          Edit
                        </Button>
                        <Button 
                          size="small" 
                          variant="outlined" 
                          color="error"
                        >
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Transactions Tab */}
        {activeTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Inventory Transactions</Typography>
              <Button variant="contained" color="primary">New Transaction</Button>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Reference</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Notes</TableCell>
                    <TableCell>User</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>TX001</TableCell>
                    <TableCell>Receiving</TableCell>
                    <TableCell>PO001</TableCell>
                    <TableCell>2023-06-05</TableCell>
                    <TableCell>Received beef shipment</TableCell>
                    <TableCell>Admin</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>TX002</TableCell>
                    <TableCell>Issuing</TableCell>
                    <TableCell>Order #123</TableCell>
                    <TableCell>2023-06-05</TableCell>
                    <TableCell>Issued ingredients for burger preparation</TableCell>
                    <TableCell>Staff</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Units Tab */}
        {activeTab === 2 && (
          <Box sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Units of Measure</Typography>
              <Button variant="contained" color="primary">Add Unit</Button>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Abbreviation</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {units.map((unit) => (
                    <TableRow key={unit.id}>
                      <TableCell>{unit.id}</TableCell>
                      <TableCell>{unit.name}</TableCell>
                      <TableCell>{unit.abbreviation}</TableCell>
                      <TableCell>
                        <Button size="small" variant="outlined" sx={{ mr: 1 }}>
                          Edit
                        </Button>
                        <Button size="small" variant="outlined" color="error">
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Low Stock Tab */}
        {activeTab === 3 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6">Low Stock Items</Typography>
            
            <TableContainer sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Current Stock</TableCell>
                    <TableCell>Unit</TableCell>
                    <TableCell>Min Stock</TableCell>
                    <TableCell>Supplier</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {inventoryItems
                    .filter(item => item.current_stock <= item.min_stock)
                    .map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.name}</TableCell>
                        <TableCell>{item.current_stock}</TableCell>
                        <TableCell>{item.unit}</TableCell>
                        <TableCell>{item.min_stock}</TableCell>
                        <TableCell>{item.supplier}</TableCell>
                        <TableCell>
                          <Button variant="contained" color="primary" size="small">
                            Reorder
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Paper>

      {/* Dialog for adding/editing inventory items */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'add' ? 'Add Inventory Item' : 'Edit Inventory Item'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="dense"
              label="Name"
              fullWidth
              variant="outlined"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <TextField
              margin="dense"
              label="Category"
              fullWidth
              variant="outlined"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
            <Box display="flex" gap={2} sx={{ mt: 2 }}>
              <TextField
                margin="dense"
                label="Current Stock"
                type="number"
                fullWidth
                variant="outlined"
                value={currentStock}
                onChange={(e) => setCurrentStock(e.target.value)}
                required
              />
              <FormControl fullWidth margin="dense">
                <InputLabel>Unit</InputLabel>
                <Select
                  value={unit}
                  label="Unit"
                  onChange={(e) => setUnit(e.target.value)}
                  required
                >
                  {units.map((u) => (
                    <MenuItem key={u.id} value={u.abbreviation}>
                      {u.abbreviation} ({u.name})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
            <Box display="flex" gap={2} sx={{ mt: 2 }}>
              <TextField
                margin="dense"
                label="Unit Cost (Birr)"
                type="number"
                fullWidth
                variant="outlined"
                value={unitCost}
                onChange={(e) => setUnitCost(e.target.value)}
                required
              />
              <TextField
                margin="dense"
                label="Minimum Stock"
                type="number"
                fullWidth
                variant="outlined"
                value={minStock}
                onChange={(e) => setMinStock(e.target.value)}
              />
            </Box>
            <TextField
              margin="dense"
              label="Supplier"
              fullWidth
              variant="outlined"
              value={supplier}
              onChange={(e) => setSupplier(e.target.value)}
            />
            <TextField
              margin="dense"
              label="Category Type"
              fullWidth
              variant="outlined"
              value={categoryType}
              onChange={(e) => setCategoryType(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {dialogMode === 'add' ? 'Add' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Inventory;