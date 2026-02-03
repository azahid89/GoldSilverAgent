import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage'; // defaults to localStorage for web
import { combineReducers } from '@reduxjs/toolkit';

import predictionsReducer from './slices/predictionsSlice';
import chatReducer from './slices/chatSlice';
import pricesReducer from './slices/pricesSlice';

// Persist configuration
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['predictions', 'chat', 'prices'], // Only persist these slices
};

// Combine reducers
const rootReducer = combineReducers({
  predictions: predictionsReducer,
  chat: chatReducer,
  prices: pricesReducer,
});

// Create persisted reducer
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configure store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types for redux-persist
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export const persistor = persistStore(store);



