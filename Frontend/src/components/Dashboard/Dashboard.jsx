import React from 'react';
import { StatCards } from './StatCards';
import { HealthOverviewTable } from './HealthOverviewTable';
import { LayoutDashboard, Sparkles } from 'lucide-react';
import './Dashboard.css';

export const Dashboard = () => {
  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <LayoutDashboard size={28} />
            Smart Agriculture Dashboard
          </h1>
          <p className="page-subtitle">
            Real-time IoT sensors monitor, automated deep learning telemetry, and crop health status overview.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '0.65rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Sparkles size={18} color="var(--accent-emerald)" />
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            AI Telemetry Engine: Active & Syncing
          </span>
        </div>
      </div>

      {/* Summary Cards */}
      <StatCards />

      {/* Health Overview Table */}
      <HealthOverviewTable />
    </div>
  );
};
