import React from 'react';
import {
  Container,
  Typography,
  Grid,
  Paper,
  Box,
} from '@mui/material';
import {
  AttachMoney as RevenueIcon,
  Restaurant as MenuIcon,
  Inventory as InventoryIcon,
  People as UsersIcon,
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Box display="flex" alignItems="center">
              <RevenueIcon fontSize="large" color="primary" />
              <Box ml={2}>
                <Typography variant="h6">Total Sales</Typography>
                <Typography variant="h4">125,000</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Box display="flex" alignItems="center">
              <MenuIcon fontSize="large" color="secondary" />
              <Box ml={2}>
                <Typography variant="h6">Menu Items</Typography>
                <Typography variant="h4">42</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Box display="flex" alignItems="center">
              <InventoryIcon fontSize="large" color="success" />
              <Box ml={2}>
                <Typography variant="h6">Inventory Items</Typography>
                <Typography variant="h4">128</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 140 }}>
            <Box display="flex" alignItems="center">
              <UsersIcon fontSize="large" color="info" />
              <Box ml={2}>
                <Typography variant="h6">Users</Typography>
                <Typography variant="h4">8</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        {/* Charts and Data */}
        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Sales Trend
            </Typography>
            <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography variant="body1" color="textSecondary">
                Sales chart will be displayed here
              </Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 2, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Top Selling Items
            </Typography>
            <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography variant="body1" color="textSecondary">
                Top selling items chart will be displayed here
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;