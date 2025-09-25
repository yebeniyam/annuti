// App.js - Main mobile application component
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaView, StyleSheet } from 'react-native';
import { AuthProvider } from './src/context/AuthContext';

// Import screens
import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import OrderScreen from './src/screens/OrderScreen';
import TableScreen from './src/screens/TableScreen';

const Stack = createStackNavigator();

const App = () => {
  return (
    <AuthProvider>
      <SafeAreaView style={styles.container}>
        <NavigationContainer>
          <Stack.Navigator initialRouteName="Login">
            <Stack.Screen 
              name="Login" 
              component={LoginScreen} 
              options={{ headerShown: false }} 
            />
            <Stack.Screen 
              name="Home" 
              component={HomeScreen} 
              options={{ title: 'Waiter Dashboard' }} 
            />
            <Stack.Screen 
              name="Order" 
              component={OrderScreen} 
              options={{ title: 'Order Details' }} 
            />
            <Stack.Screen 
              name="Table" 
              component={TableScreen} 
              options={{ title: 'Table Details' }} 
            />
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaView>
    </AuthProvider>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});

export default App;