import React, { useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  Grid,
  Tabs,
  Tab,
  TextField,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Types for reports
interface SalesSummary {
  date: string;
  total_sales: number;
  total_tax: number;
  total_discount: number;
  total_net: number;
  total_orders: number;
  avg_order_value: number;
}

interface MenuItemSales {
  id: string;
  name: string;
  sold: number;
  revenue: number;
  cost: number;
  profit: number;
  margin: number;
}

interface EmployeePerformance {
  id: string;
  name: string;
  orders_handled: number;
  total_sales: number;
  avg_order_value: number;
}

const Reports: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [dateRange, setDateRange] = useState({
    startDate: '2023-06-01',
    endDate: '2023-06-30',
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Sample data - would normally come from API
  const [salesData] = useState<SalesSummary[]>([
    { date: '2023-06-01', total_sales: 48500, total_tax: 6500, total_discount: 2000, total_net: 40000, total_orders: 45, avg_order_value: 1078 },
    { date: '2023-06-02', total_sales: 52300, total_tax: 7100, total_discount: 1800, total_net: 43400, total_orders: 48, avg_order_value: 1089 },
    { date: '2023-06-03', total_sales: 39200, total_tax: 5200, total_discount: 1500, total_net: 32500, total_orders: 36, avg_order_value: 903 },
    { date: '2023-06-04', total_sales: 61500, total_tax: 8200, total_discount: 2200, total_net: 51100, total_orders: 55, avg_order_value: 1113 },
    { date: '2023-06-05', total_sales: 55700, total_tax: 7400, total_discount: 1800, total_net: 46500, total_orders: 50, avg_order_value: 1114 },
  ]);

  const [topSellingItems] = useState<MenuItemSales[]>([
    { id: '1', name: 'Beef Burger', sold: 120, revenue: 30000, cost: 14400, profit: 15600, margin: 52 },
    { id: '2', name: 'Veggie Wrap', sold: 85, revenue: 17000, cost: 6800, profit: 10200, margin: 60 },
    { id: '3', name: 'Coke', sold: 300, revenue: 12000, cost: 3600, profit: 8400, margin: 70 },
    { id: '4', name: 'French Fries', sold: 150, revenue: 12000, cost: 3000, profit: 9000, margin: 75 },
    { id: '5', name: 'Chicken Burger', sold: 95, revenue: 20900, cost: 11400, profit: 9500, margin: 45 },
  ]);

  const [employeePerformance] = useState<EmployeePerformance[]>([
    { id: '1', name: 'Selam', orders_handled: 28, total_sales: 18200, avg_order_value: 650 },
    { id: '2', name: 'Abebe', orders_handled: 22, total_sales: 14300, avg_order_value: 650 },
    { id: '3', name: 'Chaltu', orders_handled: 18, total_sales: 12800, avg_order_value: 711 },
    { id: '4', name: 'Kebede', orders_handled: 15, total_sales: 9800, avg_order_value: 653 },
  ]);

  // Data for charts
  const paymentMethodData = [
    { name: 'Cash', value: 22000 },
    { name: 'TeleBirr', value: 18000 },
    { name: 'Chapa', value: 8500 },
    { name: 'Card', value: 10000 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Reports & Analytics
      </Typography>

      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Sales Report" />
            <Tab label="Menu Performance" />
            <Tab label="Employee Performance" />
            <Tab label="Inventory Variance" />
          </Tabs>
          
          <Box display="flex" gap={2}>
            <TextField
              label="Start Date"
              type="date"
              value={dateRange.startDate}
              onChange={(e) => setDateRange({...dateRange, startDate: e.target.value})}
              InputLabelProps={{
                shrink: true,
              }}
            />
            <TextField
              label="End Date"
              type="date"
              value={dateRange.endDate}
              onChange={(e) => setDateRange({...dateRange, endDate: e.target.value})}
              InputLabelProps={{
                shrink: true,
              }}
            />
            <Button variant="contained" color="primary">Generate Report</Button>
          </Box>
        </Box>

        {/* Sales Report Tab */}
        {activeTab === 0 && (
          <Box sx={{ p: 2 }}>
            <Grid container spacing={3} mb={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary">Total Sales</Typography>
                    <Typography variant="h5">257,200 Birr</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary">Total Orders</Typography>
                    <Typography variant="h5">234</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary">Avg Order Value</Typography>
                    <Typography variant="h5">1,100 Birr</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary">Profit Margin</Typography>
                    <Typography variant="h5">62%</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Paper elevation={2} sx={{ p: 2, height: 300 }}>
                  <Typography variant="h6" gutterBottom>Sales Trend</Typography>
                  <ResponsiveContainer width="100%" height="90%">
                    <BarChart data={salesData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="total_sales" fill="#8884d8" name="Total Sales" />
                      <Bar dataKey="total_net" fill="#82ca9d" name="Net Sales" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Paper elevation={2} sx={{ p: 2, height: 300 }}>
                  <Typography variant="h6" gutterBottom>Payment Methods</Typography>
                  <ResponsiveContainer width="100%" height="80%">
                    <PieChart>
                      <Pie
                        data={paymentMethodData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {paymentMethodData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [`${value} Birr`, 'Amount']} />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>

            <Box mt={3}>
              <Typography variant="h6" gutterBottom>Daily Sales Breakdown</Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Total Sales</TableCell>
                      <TableCell>Net Sales</TableCell>
                      <TableCell>Orders</TableCell>
                      <TableCell>Avg Order Value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {salesData.map((day, index) => (
                      <TableRow key={index}>
                        <TableCell>{day.date}</TableCell>
                        <TableCell>{day.total_sales.toLocaleString()} Birr</TableCell>
                        <TableCell>{day.total_net.toLocaleString()} Birr</TableCell>
                        <TableCell>{day.total_orders}</TableCell>
                        <TableCell>{day.avg_order_value} Birr</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </Box>
        )}

        {/* Menu Performance Tab */}
        {activeTab === 1 && (
          <Box sx={{ p: 2 }}>
            <Grid container spacing={3} mb={3}>
              <Grid item xs={12} md={8}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Top Selling Items</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={topSellingItems}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Bar yAxisId="left" dataKey="sold" name="Units Sold" fill="#8884d8" />
                      <Bar yAxisId="right" dataKey="profit" name="Profit (Birr)" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Profit Margins</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={topSellingItems}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis unit="%" />
                      <Tooltip />
                      <Bar dataKey="margin" name="Profit Margin %" fill="#00C49F" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>

            <Box>
              <Typography variant="h6" gutterBottom>Menu Item Performance</Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Item</TableCell>
                      <TableCell align="right">Sold</TableCell>
                      <TableCell align="right">Revenue</TableCell>
                      <TableCell align="right">Cost</TableCell>
                      <TableCell align="right">Profit</TableCell>
                      <TableCell align="right">Margin %</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {topSellingItems.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{item.name}</TableCell>
                        <TableCell align="right">{item.sold}</TableCell>
                        <TableCell align="right">{item.revenue.toLocaleString()} Birr</TableCell>
                        <TableCell align="right">{item.cost.toLocaleString()} Birr</TableCell>
                        <TableCell align="right">{item.profit.toLocaleString()} Birr</TableCell>
                        <TableCell align="right">{item.margin}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </Box>
        )}

        {/* Employee Performance Tab */}
        {activeTab === 2 && (
          <Box sx={{ p: 2 }}>
            <Grid container spacing={3} mb={3}>
              <Grid item xs={12}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>Employee Performance</Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={employeePerformance}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Bar yAxisId="left" dataKey="total_sales" name="Total Sales (Birr)" fill="#8884d8" />
                      <Bar yAxisId="right" dataKey="orders_handled" name="Orders Handled" fill="#82ca9d" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>

            <Box>
              <Typography variant="h6" gutterBottom>Staff Performance Details</Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Staff Name</TableCell>
                      <TableCell align="right">Orders Handled</TableCell>
                      <TableCell align="right">Total Sales</TableCell>
                      <TableCell align="right">Avg Order Value</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {employeePerformance.map((employee, index) => (
                      <TableRow key={index}>
                        <TableCell>{employee.name}</TableCell>
                        <TableCell align="right">{employee.orders_handled}</TableCell>
                        <TableCell align="right">{employee.total_sales.toLocaleString()} Birr</TableCell>
                        <TableCell align="right">{employee.avg_order_value} Birr</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </Box>
        )}

        {/* Inventory Variance Tab */}
        {activeTab === 3 && (
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Inventory Variance Report</Typography>
            
            <TableContainer sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Ingredient</TableCell>
                    <TableCell align="right">Theoretical Usage</TableCell>
                    <TableCell align="right">Actual Count</TableCell>
                    <TableCell align="right">Variance</TableCell>
                    <TableCell align="right">% Variance</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Beef</TableCell>
                    <TableCell align="right">15.2 kg</TableCell>
                    <TableCell align="right">14.1 kg</TableCell>
                    <TableCell align="right" sx={{ color: 'error.main' }}>-1.1 kg</TableCell>
                    <TableCell align="right" sx={{ color: 'error.main' }}>-7.2%</TableCell>
                    <TableCell><span style={{ color: 'error.main' }}>Critical</span></TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Cheese</TableCell>
                    <TableCell align="right">3.0 kg</TableCell>
                    <TableCell align="right">2.95 kg</TableCell>
                    <TableCell align="right" sx={{ color: 'warning.main' }}>-0.05 kg</TableCell>
                    <TableCell align="right" sx={{ color: 'warning.main' }}>-1.7%</TableCell>
                    <TableCell><span style={{ color: 'warning.main' }}>Warning</span></TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Lettuce</TableCell>
                    <TableCell align="right">5.5 kg</TableCell>
                    <TableCell align="right">5.6 kg</TableCell>
                    <TableCell align="right" sx={{ color: 'success.main' }}>+0.1 kg</TableCell>
                    <TableCell align="right" sx={{ color: 'success.main' }}>+1.8%</TableCell>
                    <TableCell><span style={{ color: 'success.main' }}>OK</span></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
            
            <Box mt={3}>
              <Typography variant="h6" gutterBottom>Waste Report</Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Ingredient</TableCell>
                      <TableCell>Quantity Wasted</TableCell>
                      <TableCell>Unit</TableCell>
                      <TableCell>Cost</TableCell>
                      <TableCell>Reason</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>2023-06-05</TableCell>
                      <TableCell>Beef</TableCell>
                      <TableCell>0.5</TableCell>
                      <TableCell>kg</TableCell>
                      <TableCell>310 Birr</TableCell>
                      <TableCell>Expired</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>2023-06-04</TableCell>
                      <TableCell>Lettuce</TableCell>
                      <TableCell>0.3</TableCell>
                      <TableCell>kg</TableCell>
                      <TableCell>24 Birr</TableCell>
                      <TableCell>Wilted</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default Reports;