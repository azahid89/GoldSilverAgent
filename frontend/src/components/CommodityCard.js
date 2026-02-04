import React, { useState } from 'react';
import './CommodityCard.css';
import { ChevronDown, ChevronUp } from 'lucide-react';

const CommodityCard = ({ commodity, prediction, getSignalIcon, getSignalColor }) => {
  const [expanded, setExpanded] = useState(false);

  if (!prediction) return null;

  const signal = prediction.signal || 'neutral';
  const confidence = prediction.confidence || 0;
  const drivers = prediction.drivers || [];
  const agentBreakdown = prediction.agent_breakdown || {};
  const invalidation = prediction.invalidation_conditions || [];

  return (
    <div className="commodity-card">
      <div className="card-header">
        <div className="card-title-section">
          <h3>{commodity}</h3>
          <div className="signal-badge" style={{ color: getSignalColor(signal) }}>
            {getSignalIcon(signal)}
            <span>{signal.toUpperCase()}</span>
          </div>
        </div>
        <div className="confidence-meter">
          <div className="confidence-label">Confidence</div>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{
                width: `${confidence}%`,
                backgroundColor: getSignalColor(signal),
              }}
            />
          </div>
          <div className="confidence-value">{confidence.toFixed(1)}%</div>
        </div>
      </div>

      <div className="card-body">
        <div className="drivers-section">
          <h4>Key Drivers</h4>
          <ul>
            {drivers.slice(0, 3).map((driver, idx) => (
              <li key={idx}>{driver}</li>
            ))}
          </ul>
        </div>

        <button
          className="expand-btn"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <>
              <span>Show Less</span>
              <ChevronUp size={16} />
            </>
          ) : (
            <>
              <span>Show More</span>
              <ChevronDown size={16} />
            </>
          )}
        </button>

        {expanded && (
          <div className="expanded-content">
            <div className="agent-breakdown">
              <h4>Agent Breakdown</h4>
              <div className="agent-list">
                {Object.entries(agentBreakdown).map(([agent, data]) => (
                  <div key={agent} className="agent-item">
                    <span className="agent-name">{agent}</span>
                    <span
                      className="agent-signal"
                      style={{ color: getSignalColor(data.signal) }}
                    >
                      {data.signal}
                    </span>
                    <span className="agent-confidence">
                      {data.confidence?.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {invalidation.length > 0 && (
              <div className="invalidation-section">
                <h4>Invalidation Conditions</h4>
                <ul>
                  {invalidation.slice(0, 5).map((condition, idx) => (
                    <li key={idx}>{condition}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CommodityCard;





