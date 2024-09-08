"use client"

import React from 'react';
import HomePage from './HomePage';
import { Provider } from 'react-redux';
import store from './store';

function App() {
  return (
    <HomePage />
  );
}

export default function WrappedApp(props: any) {
  return (
    <Provider store={store}>
      <App {...props} />
    </Provider>
  );
}
