import React from 'react';
import { useApp } from '../../context/AppContext';
import { Sprout, CheckCircle, AlertTriangle, AlertOctagon } from 'lucide-react';

export const StatCards = () => {
  const { plants } = useApp();

  const total = plants.length;
  const healthy = plants.filter(p => p.status === 'Healthy' || p.status === 'Good').length;
  const attention = plants.filter(p => p.status === 'Needs Attention').length;
  const critical = plants.filter(p => p.status === 'Critical').length;

  return (
    <div className="stat-cards-grid">
      <div className="glass-card stat-card">
        <div className="stat-icon-wrapper stat-icon-total">
          <Sprout size={28} />
        </div>
        <div className="stat-info">
          <span className="stat-value">{total}</span>
          <span className="stat-label">Total Plants</span>
        </div>
      </div>

      <div className="glass-card stat-card">
        <div className="stat-icon-wrapper stat-icon-healthy">
          <CheckCircle size={28} />
        </div>
        <div className="stat-info">
          <span className="stat-value">{healthy}</span>
          <span className="stat-label">Healthy Plants</span>
        </div>
      </div>

      <div className="glass-card stat-card">
        <div className="stat-icon-wrapper stat-icon-warning">
          <AlertTriangle size={28} />
        </div>
        <div className="stat-info">
          <span className="stat-value">{attention}</span>
          <span className="stat-label">Plants Needed Attention</span>
        </div>
      </div>

      <div className="glass-card stat-card">
        <div className="stat-icon-wrapper stat-icon-critical">
          <AlertOctagon size={28} />
        </div>
        <div className="stat-info">
          <span className="stat-value">{critical}</span>
          <span className="stat-label">Critical Plants</span>
        </div>
      </div>
    </div>
  );
};
