// src/screens/TableScreen.js
import React from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
} from 'react-native';

// Sample order data - would normally come from API
const sampleOrders = [
  { id: '1', item: 'Beef Burger', quantity: 2, status: 'preparing', price: 250 },
  { id: '2', item: 'Coke 330ml', quantity: 4, status: 'ready', price: 40 },
  { id: '3', item: 'French Fries', quantity: 1, status: 'new', price: 80 },
];

const TableScreen = ({ route, navigation }) => {
  const { table } = route.params;

  const getStatusColor = (status) => {
    switch (status) {
      case 'new':
        return '#2196f3'; // Blue
      case 'preparing':
        return '#ff9800'; // Orange
      case 'ready':
        return '#4caf50'; // Green
      case 'served':
        return '#9c27b0'; // Purple
      default:
        return '#9e9e9e'; // Gray
    }
  };

  const renderOrderItem = ({ item }) => (
    <View style={styles.orderItem}>
      <View style={styles.orderInfo}>
        <Text style={styles.itemName}>{item.quantity}x {item.item}</Text>
        <Text style={styles.itemPrice}>{item.price * item.quantity} Birr</Text>
      </View>
      <View style={styles.orderStatus}>
        <Text style={[styles.statusText, { color: getStatusColor(item.status) }]}>
          {item.status}
        </Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.tableName}>{table.name}</Text>
        <Text style={styles.guestCount}>{table.guests} {table.guests === 1 ? 'Guest' : 'Guests'}</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Current Orders</Text>
        <FlatList
          data={sampleOrders}
          renderItem={renderOrderItem}
          keyExtractor={item => item.id}
          contentContainerStyle={styles.ordersList}
        />
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.actionButton, styles.addButton]}
          onPress={() => navigation.navigate('Order', { table })}
        >
          <Text style={styles.actionButtonText}>Add Item</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, styles.billButton]}
          onPress={() => alert('Bill requested for ' + table.name)}
        >
          <Text style={styles.actionButtonText}>Request Bill</Text>
        </TouchableOpacity>
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
  tableName: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  guestCount: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
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
  ordersList: {
    paddingBottom: 10,
  },
  orderItem: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  orderInfo: {
    flex: 1,
  },
  itemName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  itemPrice: {
    fontSize: 14,
    color: '#666',
    marginTop: 3,
  },
  orderStatus: {
    alignItems: 'flex-end',
  },
  statusText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  actions: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: '#fff',
  },
  actionButton: {
    flex: 1,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  addButton: {
    backgroundColor: '#4caf50',
  },
  billButton: {
    backgroundColor: '#2196f3',
  },
  actionButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default TableScreen;