import React from 'react';
import { useApp } from '../../context/AppContext';
import { Sun, Moon, Bell, ChevronRight } from 'lucide-react';
import './Navbar.css';

export const Navbar = () => {
  const { theme, toggleTheme, activeTab, setActiveTab, alerts, growerProfile } = useApp();

  const getPageTitle = () => {
    switch (activeTab) {
      case 'dashboard': return 'Dashboard & Health Overview';
      case 'my-plants': return 'My Connected Plants';
      case 'plant-detail': return 'Plant Telemetry & Growth Details';
      case 'alerts': return 'Alerts & Automated Remedies';
      case 'disease-detection': return 'AI Disease Detection Engine';
      case 'settings': return 'Grower Profile & App Settings';
      default: return 'Dashboard';
    }
  };

  return (
    <header className="navbar">
      <div className="navbar-left">
        <div className="navbar-breadcrumb">
          <span>AgriSmart</span>
          <ChevronRight size={14} />
          <span className="navbar-page-name">{getPageTitle()}</span>
        </div>
      </div>

      <div className="navbar-right">
        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Bright' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? (
            <>
              <Sun size={16} color="var(--status-warning)" />
              <span>Bright Schema</span>
            </>
          ) : (
            <>
              <Moon size={16} color="var(--accent-emerald)" />
              <span>Dark Schema</span>
            </>
          )}
        </button>

        <button
          className="notification-bell-btn"
          onClick={() => setActiveTab('alerts')}
          title="View Active Alerts"
        >
          <Bell size={18} />
          {alerts.length > 0 && (
            <span className="bell-badge">{alerts.length}</span>
          )}
        </button>
      </div>
    </header>
  );
};
