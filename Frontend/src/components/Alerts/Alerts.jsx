import React from 'react';
import { useApp } from '../../context/AppContext';
import { AlertTriangle, AlertOctagon, Info, Sparkles, CheckCircle2, Zap, Sprout } from 'lucide-react';
import './Alerts.css';

export const Alerts = () => {
  const { alerts, applyRemedy, navigateToPlantDetail } = useApp();

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <AlertTriangle size={28} />
            Smart Alerts & Proposed Remedies
          </h1>
          <p className="page-subtitle">
            Monitors Temperature, pH, Water Level, and Humidity anomalies with automated IoT solution remedies.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '0.65rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Sparkles size={18} color="var(--accent-emerald)" />
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            AI Remedy Recommender Active
          </span>
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem' }}>
          <CheckCircle2 size={48} color="var(--status-healthy)" style={{ margin: '0 auto 1rem' }} />
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>All Systems Nominal!</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
            There are currently no temperature, pH, humidity, or water level anomalies across your crops.
          </p>
        </div>
      ) : (
        <div className="alerts-list">
          {alerts.map((alert) => {
            const isCritical = alert.severity === 'critical';
            const isWarning = alert.severity === 'warning';

            return (
              <div key={alert.id} className={`glass-card alert-card ${alert.severity}`}>
                <div className="alert-header">
                  <div className="alert-title-group">
                    {isCritical ? (
                      <AlertOctagon size={24} color="var(--status-critical)" />
                    ) : isWarning ? (
                      <AlertTriangle size={24} color="var(--status-warning)" />
                    ) : (
                      <Info size={24} color="var(--accent-emerald)" />
                    )}
                    <div>
                      <h3 className="alert-title">{alert.title}</h3>
                      <div className="alert-plant-tag" onClick={() => navigateToPlantDetail(alert.plantId)} style={{ cursor: 'pointer' }}>
                        <Sprout size={14} color="var(--accent-emerald)" />
                        <span>{alert.plantName}</span>
                        <span style={{ color: 'var(--text-muted)' }}>• {alert.timestamp}</span>
                      </div>
                    </div>
                  </div>

                  <span className={`badge ${isCritical ? 'badge-critical' : isWarning ? 'badge-warning' : 'badge-good'}`}>
                    {alert.type}
                  </span>
                </div>

                <p className="alert-description">{alert.description}</p>

                {/* Proposed Remedy Box as required by PDF */}
                <div className="remedy-box">
                  <div className="remedy-content">
                    <Zap size={20} color="var(--accent-emerald)" style={{ marginTop: '0.15rem', flexShrink: 0 }} />
                    <div>
                      <div className="remedy-title">PROPOSED SUITABLE REMEDY</div>
                      <div className="remedy-text">{alert.remedyText}</div>
                    </div>
                  </div>

                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => applyRemedy(alert.id)}
                  >
                    <CheckCircle2 size={16} />
                    <span>Apply Remedy Now</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
