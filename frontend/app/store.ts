import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import { thunk } from 'redux-thunk';
import rootReducer from './reducers'; // Adjust the path if necessary

// Define the RootState and AppDispatch types
export type RootState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch;

// Create the store
const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(thunk),
});

// Export the store
export default store;