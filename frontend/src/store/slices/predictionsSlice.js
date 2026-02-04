import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import API_BASE_URL from '../../config';

// Async thunk for fetching predictions
export const fetchPredictions = createAsyncThunk(
  'predictions/fetchPredictions',
  async (horizon = 90) => {
    const response = await fetch(`${API_BASE_URL}/api/predictions?horizon=${horizon}`);
    if (!response.ok) {
      throw new Error('Failed to fetch predictions');
    }
    const data = await response.json();
    return data;
  }
);

const predictionsSlice = createSlice({
  name: 'predictions',
  initialState: {
    gold: null,
    silver: null,
    loading: false,
    error: null,
    lastUpdated: null,
    horizon: 90,
  },
  reducers: {
    setHorizon: (state, action) => {
      state.horizon = action.payload;
    },
    clearPredictions: (state) => {
      state.gold = null;
      state.silver = null;
      state.lastUpdated = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPredictions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPredictions.fulfilled, (state, action) => {
        state.loading = false;
        state.gold = action.payload.gold;
        state.silver = action.payload.silver;
        state.lastUpdated = new Date().toISOString();
        state.error = null;
      })
      .addCase(fetchPredictions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export const { setHorizon, clearPredictions } = predictionsSlice.actions;
export default predictionsSlice.reducer;





