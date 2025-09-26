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
import { MenuItem as MenuItemType } from '../types/menu';
import { 
  fetchMenuItems, 
  addMenuItem, 
  updateMenuItem,
  fetchCategories
} from '../features/menu/menuSlice';

const MenuManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<'add' | 'edit'>('add');
  const [currentItem, setCurrentItem] = useState<MenuItemType | null>(null);
  
  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [cost, setCost] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [isAvailable, setIsAvailable] = useState(true);
  const [prepTime, setPrepTime] = useState('');
  
  const dispatch = useDispatch<AppDispatch>();
  const { items, categories, error } = useSelector((state: RootState) => state.menu);

  useEffect(() => {
    // Fetch data when component mounts
    dispatch(fetchMenuItems());
    dispatch(fetchCategories());
  }, [dispatch]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleOpenDialog = (mode: 'add' | 'edit', item?: MenuItemType) => {
    setDialogMode(mode);
    
    if (mode === 'edit' && item) {
      setCurrentItem(item);
      setName(item.name);
      setDescription(item.description);
      setPrice(item.price.toString());
      setCost(item.cost.toString());
      setCategoryId(item.category_id);
      setIsAvailable(item.is_available);
      setPrepTime(item.prep_time?.toString() || '');
    } else {
      // Reset form for adding new item
      setCurrentItem(null);
      setName('');
      setDescription('');
      setPrice('');
      setCost('');
      setCategoryId('');
      setIsAvailable(true);
      setPrepTime('');
    }
    
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (dialogMode === 'add') {
        const newItem: Omit<MenuItemType, 'id'> = {
          name,
          description: description || '',
          price: parseFloat(price),
          cost: parseFloat(cost),
          category_id: categoryId,
          category_name: categories.find(cat => cat.id === categoryId)?.name || 'Uncategorized',
          is_available: isAvailable,
          prep_time: prepTime ? parseInt(prepTime) : undefined,
        };
        
        await dispatch(addMenuItem(newItem)).unwrap();
      } else if (currentItem) {
        const updatedItem: Partial<MenuItemType> = {
          name,
          description: description || '',
          price: parseFloat(price),
          cost: parseFloat(cost),
          category_id: categoryId,
          is_available: isAvailable,
          prep_time: prepTime ? parseInt(prepTime) : undefined,
        };
        
        await dispatch(updateMenuItem({
          id: currentItem.id,
          itemData: updatedItem
        })).unwrap();
      }
      
      handleCloseDialog();
    } catch (err) {
      console.error('Error saving menu item:', err);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Menu Management
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Menu Items" />
            <Tab label="Categories" />
            <Tab label="Recipes" />
          </Tabs>
        </Box>

        {/* Menu Items Tab */}
        {activeTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Menu Items</Typography>
              <Button 
                variant="contained" 
                color="primary"
                onClick={() => handleOpenDialog('add')}
              >
                Add Menu Item
              </Button>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Price (Birr)</TableCell>
                    <TableCell>COGS (Birr)</TableCell>
                    <TableCell>Profit Margin</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Prep Time (min)</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {items.map((item: MenuItemType) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.id}</TableCell>
                      <TableCell>{item.name}</TableCell>
                      <TableCell>{item.description}</TableCell>
                      <TableCell>{item.category_name}</TableCell>
                      <TableCell>{item.price}</TableCell>
                      <TableCell>{item.cost}</TableCell>
                      <TableCell>{(item.price - item.cost).toFixed(2)}</TableCell>
                      <TableCell>{item.is_available ? 'Available' : 'Not Available'}</TableCell>
                      <TableCell>{item.prep_time || '-'}</TableCell>
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

        {/* Categories Tab */}
        {activeTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Categories</Typography>
              <Button variant="contained" color="primary">Add Category</Button>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Display Order</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {categories.map((category) => (
                    <TableRow key={category.id}>
                      <TableCell>{category.id}</TableCell>
                      <TableCell>{category.name}</TableCell>
                      <TableCell>{category.description}</TableCell>
                      <TableCell>{category.display_order}</TableCell>
                      <TableCell>{category.is_active ? 'Active' : 'Inactive'}</TableCell>
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

        {/* Recipes Tab - Simplified for now */}
        {activeTab === 2 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6">Recipe Management</Typography>
            <Typography variant="body1" color="textSecondary" sx={{ mt: 2 }}>
              Recipe builder functionality will be implemented here to define ingredients and quantities for each menu item,
              allowing for COGS calculation.
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Dialog for adding/editing menu items */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'add' ? 'Add Menu Item' : 'Edit Menu Item'}
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
              label="Description"
              fullWidth
              variant="outlined"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <Box display="flex" gap={2} sx={{ mt: 2 }}>
              <TextField
                margin="dense"
                label="Price (Birr)"
                type="number"
                fullWidth
                variant="outlined"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
              />
              <TextField
                margin="dense"
                label="Cost (Birr)"
                type="number"
                fullWidth
                variant="outlined"
                value={cost}
                onChange={(e) => setCost(e.target.value)}
                required
              />
            </Box>
            <Box display="flex" gap={2} sx={{ mt: 2 }}>
              <FormControl fullWidth margin="dense">
                <InputLabel>Category</InputLabel>
                <Select
                  value={categoryId}
                  label="Category"
                  onChange={(e) => setCategoryId(e.target.value as string)}
                  required
                >
                  {categories.map((category) => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                margin="dense"
                label="Prep Time (min)"
                type="number"
                fullWidth
                variant="outlined"
                value={prepTime}
                onChange={(e) => setPrepTime(e.target.value)}
              />
            </Box>
            <Box display="flex" alignItems="center" sx={{ mt: 2 }}>
              <label>
                <input
                  type="checkbox"
                  checked={isAvailable}
                  onChange={(e) => setIsAvailable(e.target.checked)}
                />
                Available for Order
              </label>
            </Box>
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

export default MenuManagement;