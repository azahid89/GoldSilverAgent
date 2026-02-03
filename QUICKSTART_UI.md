# Quick Start Guide - React UI

## Prerequisites

- Node.js 16+ installed
- Python virtual environment set up (see main README)
- Backend dependencies installed

## Setup Steps

### 1. Install Backend Dependencies

```bash
# Make sure you're in the project root
source venv/bin/activate
pip install flask flask-cors
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Start the Backend API

In terminal 1:
```bash
# From project root
./start_api.sh
```

You should see:
```
Starting API server on http://localhost:5000
```

### 4. Start the React Frontend

In terminal 2:
```bash
cd frontend
npm start
```

The browser should automatically open to `http://localhost:3000`

## Using the UI

### Dashboard Tab
- View real-time predictions for Gold and Silver
- Click "Show More" to see agent breakdowns
- Click "Refresh" to get latest predictions
- See confidence meters and key drivers

### Chat Tab
- Type questions in the input box
- Press Enter or click Send
- Get instant responses from the agent

### Example Questions
- "What's the gold prediction?"
- "Show me silver 30-day forecast"
- "What are the drivers for gold?"
- "Explain why silver is bullish"
- "Gold 7-day prediction"
- "What factors affect silver prices?"

## Troubleshooting

### Port 3000 already in use
```bash
# Kill the process or use a different port
PORT=3001 npm start
```

### API connection errors
- Make sure the backend is running on port 5000
- Check browser console for errors
- Verify Flask is installed: `pip list | grep flask`

### CORS errors
- Make sure `flask-cors` is installed
- Check that the API is running

### Frontend won't compile
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Check Node.js version: `node --version` (should be 16+)

## Features

✅ Real-time dashboard with predictions
✅ ChatGPT-like chat interface
✅ Agent breakdown visualization
✅ Confidence meters
✅ Key drivers display
✅ Responsive design
✅ Dark theme UI

Enjoy your Gold & Silver Agent Dashboard! 🏅



