import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Async thunk for fetching current prices
export const fetchPrices = createAsyncThunk(
  'prices/fetchPrices',
  async () => {
    const response = await fetch('/api/prices');
    if (!response.ok) {
      throw new Error('Failed to fetch prices');
    }
    const data = await response.json();
    return data;
  }
);

const pricesSlice = createSlice({
  name: 'prices',
  initialState: {
    gold: null,
    silver: null,
    loading: false,
    error: null,
    lastUpdated: null,
  },
  reducers: {
    clearPrices: (state) => {
      state.gold = null;
      state.silver = null;
      state.lastUpdated = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPrices.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPrices.fulfilled, (state, action) => {
        state.loading = false;
        state.gold = action.payload.gold;
        state.silver = action.payload.silver;
        state.lastUpdated = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchPrices.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearPrices } = pricesSlice.actions;
export default pricesSlice.reducer;

