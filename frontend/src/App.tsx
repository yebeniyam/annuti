import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store';
import './App.css';
import AppContent from './AppContent';

function App() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
}

export default App;