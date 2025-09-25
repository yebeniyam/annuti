// src/screens/HomeScreen.js
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
} from 'react-native';
import { useAuth } from '../context/AuthContext';

const HomeScreen = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [tables, setTables] = useState([]);

  // In a real app, fetch assigned tables from the API
  useEffect(() => {
    // Sample data - would normally come from API
    const sampleTables = [
      { id: '1', name: 'Table 1', guests: 4, status: 'occupied', orders: 2 },
      { id: '2', name: 'Table 2', guests: 2, status: 'occupied', orders: 1 },
      { id: '3', name: 'Table 3', guests: 6, status: 'available', orders: 0 },
      { id: '4', name: 'Table 4', guests: 2, status: 'occupied', orders: 3 },
      { id: '5', name: 'Bar Seat 1', guests: 1, status: 'available', orders: 0 },
    ];
    setTables(sampleTables);
  }, []);

  const handleTablePress = (table) => {
    navigation.navigate('Table', { table });
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', onPress: () => logout() }
      ]
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'occupied':
        return '#ff9800'; // Orange
      case 'available':
        return '#4caf50'; // Green
      case 'reserved':
        return '#2196f3'; // Blue
      case 'dirty':
        return '#9e9e9e'; // Gray
      default:
        return '#9e9e9e';
    }
  };

  const renderTableItem = ({ item }) => (
    <TouchableOpacity
      style={[styles.tableCard, { borderColor: getStatusColor(item.status) }]}
      onPress={() => handleTablePress(item)}
    >
      <View style={styles.tableHeader}>
        <Text style={styles.tableName}>{item.name}</Text>
        <Text style={styles.guestCount}>{item.guests} {item.guests === 1 ? 'guest' : 'guests'}</Text>
      </View>
      <View style={styles.tableDetails}>
        <Text style={styles.statusText}>Status: {item.status}</Text>
        <Text style={styles.orderCount}>Orders: {item.orders}</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Waiter Dashboard</Text>
        <View style={styles.userInfoContainer}>
          <Text style={styles.welcomeText}>Welcome, {user?.full_name || user?.email || 'User'}!</Text>
          <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
            <Text style={styles.logoutText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Your Tables</Text>
        <FlatList
          data={tables}
          renderItem={renderTableItem}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.listContainer}
        />
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  userInfoContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 5,
  },
  welcomeText: {
    fontSize: 16,
    color: '#666',
    flex: 1,
  },
  logoutButton: {
    backgroundColor: '#f44336',
    paddingVertical: 5,
    paddingHorizontal: 10,
    borderRadius: 5,
  },
  logoutText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  section: {
    flex: 1,
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  listContainer: {
    paddingBottom: 20,
  },
  tableCard: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  tableHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  tableName: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  guestCount: {
    fontSize: 16,
    color: '#666',
  },
  tableDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statusText: {
    fontSize: 14,
    color: '#666',
  },
  orderCount: {
    fontSize: 14,
    color: '#666',
  },
});

export default HomeScreen;