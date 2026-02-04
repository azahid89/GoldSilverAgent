import { createSlice } from '@reduxjs/toolkit';

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      {
        role: 'assistant',
        content: 'Hello! I\'m your Gold & Silver market analysis agent. Ask me about predictions, market drivers, or request analysis for specific time horizons.',
        timestamp: new Date().toISOString(),
      },
    ],
    loading: false,
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push({
        ...action.payload,
        timestamp: new Date().toISOString(),
      });
    },
    updateLastMessage: (state, action) => {
      if (state.messages.length > 0) {
        const lastMessage = state.messages[state.messages.length - 1];
        if (lastMessage.role === 'assistant') {
          lastMessage.content = action.payload.content;
        }
      }
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    clearChat: (state) => {
      state.messages = [
        {
          role: 'assistant',
          content: 'Hello! I\'m your Gold & Silver market analysis agent. Ask me about predictions, market drivers, or request analysis for specific time horizons.',
          timestamp: new Date().toISOString(),
        },
      ];
      state.loading = false;
    },
  },
});

export const { addMessage, updateLastMessage, setLoading, clearChat } = chatSlice.actions;
export default chatSlice.reducer;





