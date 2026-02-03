import { configureStore } from '@reduxjs/toolkit';
import { combineReducers } from '@reduxjs/toolkit';

import predictionsReducer from './slices/predictionsSlice';
import chatReducer from './slices/chatSlice';
import pricesReducer from './slices/pricesSlice';

// Combine reducers
const rootReducer = combineReducers({
  predictions: predictionsReducer,
  chat: chatReducer,
  prices: pricesReducer,
});

// Configure store
export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false, // simpler for non-persisted store
    }),
});



