import React from 'react';
import './Dashboard.css';
import CommodityCard from './CommodityCard';
import { RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const Dashboard = ({ predictions, loading, onRefresh }) => {
  const getSignalIcon = (signal) => {
    switch (signal?.toLowerCase()) {
      case 'bullish':
        return <TrendingUp className="signal-icon bullish" />;
      case 'bearish':
        return <TrendingDown className="signal-icon bearish" />;
      default:
        return <Minus className="signal-icon neutral" />;
    }
  };

  const getSignalColor = (signal) => {
    switch (signal?.toLowerCase()) {
      case 'bullish':
        return '#10b981';
      case 'bearish':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <RefreshCw className="spinner" />
        <p>Loading predictions...</p>
      </div>
    );
  }

  if (!predictions) {
    return (
      <div className="dashboard-error">
        <p>No predictions available. Please check the backend connection.</p>
        <button onClick={onRefresh} className="refresh-btn">
          <RefreshCw size={16} />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Market Predictions Dashboard</h2>
        <button onClick={onRefresh} className="refresh-btn">
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      <div className="dashboard-grid">
        {predictions.gold && (
          <CommodityCard
            commodity="Gold"
            prediction={predictions.gold}
            getSignalIcon={getSignalIcon}
            getSignalColor={getSignalColor}
          />
        )}
        {predictions.silver && (
          <CommodityCard
            commodity="Silver"
            prediction={predictions.silver}
            getSignalIcon={getSignalIcon}
            getSignalColor={getSignalColor}
          />
        )}
      </div>

      <div className="dashboard-summary">
        <h3>Quick Summary</h3>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="summary-label">Gold Signal:</span>
            <span
              className="summary-value"
              style={{ color: getSignalColor(predictions.gold?.signal) }}
            >
              {getSignalIcon(predictions.gold?.signal)}
              {predictions.gold?.signal?.toUpperCase() || 'N/A'}
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Gold Confidence:</span>
            <span className="summary-value">
              {predictions.gold?.confidence?.toFixed(1) || '0'}%
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Silver Signal:</span>
            <span
              className="summary-value"
              style={{ color: getSignalColor(predictions.silver?.signal) }}
            >
              {getSignalIcon(predictions.silver?.signal)}
              {predictions.silver?.signal?.toUpperCase() || 'N/A'}
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Silver Confidence:</span>
            <span className="summary-value">
              {predictions.silver?.confidence?.toFixed(1) || '0'}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

