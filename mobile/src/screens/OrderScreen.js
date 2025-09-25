// src/screens/OrderScreen.js
import React, { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
} from 'react-native';

// Sample menu items - would normally come from API
const menuItems = [
  { id: '1', name: 'Beef Burger', price: 250, category: 'Burgers' },
  { id: '2', name: 'Chicken Burger', price: 220, category: 'Burgers' },
  { id: '3', name: 'Coke 330ml', price: 40, category: 'Drinks' },
  { id: '4', name: 'Fanta 330ml', price: 40, category: 'Drinks' },
  { id: '5', name: 'French Fries', price: 80, category: 'Sides' },
  { id: '6', name: 'Onion Rings', price: 90, category: 'Sides' },
];

const OrderScreen = ({ route, navigation }) => {
  const { table } = route.params;
  const [orderItems, setOrderItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Get unique categories
  const categories = ['All', ...new Set(menuItems.map(item => item.category))];

  // Filter menu items by category
  const filteredMenuItems = selectedCategory === 'All' 
    ? menuItems 
    : menuItems.filter(item => item.category === selectedCategory);

  const addToOrder = (item) => {
    const existingItem = orderItems.find(orderItem => orderItem.id === item.id);
    
    if (existingItem) {
      // If item already exists, increment quantity
      setOrderItems(orderItems.map(orderItem => 
        orderItem.id === item.id 
          ? { ...orderItem, quantity: orderItem.quantity + 1 } 
          : orderItem
      ));
    } else {
      // Add new item to order
      setOrderItems([...orderItems, { ...item, quantity: 1 }]);
    }
  };

  const removeFromOrder = (itemId) => {
    const existingItem = orderItems.find(item => item.id === itemId);
    
    if (existingItem && existingItem.quantity > 1) {
      // If quantity > 1, decrease quantity
      setOrderItems(orderItems.map(item => 
        item.id === itemId 
          ? { ...item, quantity: item.quantity - 1 } 
          : item
      ));
    } else {
      // Otherwise, remove item completely
      setOrderItems(orderItems.filter(item => item.id !== itemId));
    }
  };

  const calculateTotal = () => {
    return orderItems.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const sendToKitchen = () => {
    // TODO: Send order to kitchen via API
    alert(`Order sent to kitchen for ${table.name}!`);
    navigation.goBack();
  };

  const renderMenuItem = ({ item }) => (
    <TouchableOpacity style={styles.menuItem} onPress={() => addToOrder(item)}>
      <View style={styles.menuItemInfo}>
        <Text style={styles.menuItemName}>{item.name}</Text>
        <Text style={styles.menuItemPrice}>{item.price} Birr</Text>
      </View>
    </TouchableOpacity>
  );

  const renderOrderItem = ({ item }) => (
    <View style={styles.orderItem}>
      <View style={styles.orderItemInfo}>
        <Text style={styles.orderItemName}>{item.name}</Text>
        <Text style={styles.orderItemPrice}>{item.price} Birr</Text>
      </View>
      <View style={styles.quantityControl}>
        <TouchableOpacity 
          style={styles.quantityButton} 
          onPress={() => removeFromOrder(item.id)}
        >
          <Text style={styles.quantityButtonText}>-</Text>
        </TouchableOpacity>
        <Text style={styles.quantity}>{item.quantity}</Text>
        <TouchableOpacity 
          style={styles.quantityButton} 
          onPress={() => addToOrder(item)}
        >
          <Text style={styles.quantityButtonText}>+</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Add Items - {table.name}</Text>
      </View>

      <View style={styles.content}>
        <View style={styles.menuSection}>
          <View style={styles.categorySelector}>
            <FlatList
              horizontal
              data={categories}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.categoryButton,
                    selectedCategory === item && styles.selectedCategoryButton
                  ]}
                  onPress={() => setSelectedCategory(item)}
                >
                  <Text
                    style={[
                      styles.categoryButtonText,
                      selectedCategory === item && styles.selectedCategoryButtonText
                    ]}
                  >
                    {item}
                  </Text>
                </TouchableOpacity>
              )}
              keyExtractor={item => item}
              showsHorizontalScrollIndicator={false}
            />
          </View>

          <FlatList
            data={filteredMenuItems}
            renderItem={renderMenuItem}
            keyExtractor={item => item.id}
            style={styles.menuList}
          />
        </View>

        <View style={styles.orderSection}>
          <Text style={styles.orderTitle}>Current Order</Text>
          
          {orderItems.length === 0 ? (
            <Text style={styles.emptyOrderText}>No items added yet</Text>
          ) : (
            <>
              <FlatList
                data={orderItems}
                renderItem={renderOrderItem}
                keyExtractor={item => item.id}
                style={styles.orderList}
              />
              
              <View style={styles.totalSection}>
                <Text style={styles.totalText}>Total: {calculateTotal()} Birr</Text>
                
                <TouchableOpacity
                  style={styles.sendToKitchenButton}
                  onPress={sendToKitchen}
                >
                  <Text style={styles.sendToKitchenButtonText}>Send to Kitchen</Text>
                </TouchableOpacity>
              </View>
            </>
          )}
        </View>
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
    fontSize: 18,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    flexDirection: 'row',
  },
  menuSection: {
    flex: 1,
    backgroundColor: '#fff',
    margin: 10,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  categorySelector: {
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  categoryButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    marginRight: 10,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
  },
  selectedCategoryButton: {
    backgroundColor: '#2196f3',
  },
  categoryButtonText: {
    color: '#333',
  },
  selectedCategoryButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  menuList: {
    flex: 1,
    padding: 10,
  },
  menuItem: {
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  menuItemInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  menuItemName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  menuItemPrice: {
    fontSize: 16,
    color: '#666',
  },
  orderSection: {
    width: '40%',
    backgroundColor: '#fff',
    margin: 10,
    borderRadius: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
  },
  orderTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  emptyOrderText: {
    textAlign: 'center',
    padding: 20,
    color: '#999',
  },
  orderList: {
    flex: 1,
    padding: 10,
  },
  orderItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  orderItemInfo: {
    flex: 1,
  },
  orderItemName: {
    fontSize: 16,
  },
  orderItemPrice: {
    fontSize: 14,
    color: '#666',
  },
  quantityControl: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  quantityButton: {
    backgroundColor: '#f0f0f0',
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
  },
  quantityButtonText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  quantity: {
    marginHorizontal: 10,
    fontSize: 16,
    fontWeight: 'bold',
  },
  totalSection: {
    padding: 15,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  totalText: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 15,
  },
  sendToKitchenButton: {
    backgroundColor: '#4caf50',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  sendToKitchenButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default OrderScreen;