import React from 'react';
import { useApp } from '../../context/AppContext';
import { LayoutDashboard, Sprout, AlertTriangle, Scan, Settings, LogOut, Cpu } from 'lucide-react';
import './Sidebar.css';

export const Sidebar = () => {
  const { activeTab, setActiveTab, growerProfile, alerts, logout } = useApp();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'my-plants', label: 'My Plants', icon: Sprout },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle, badge: alerts.length > 0 ? alerts.length : null },
    { id: 'disease-detection', label: 'Disease Detection', icon: Scan },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">
          <Cpu size={24} />
        </div>
        <div>
          <div className="sidebar-brand-title">AgriSmart AI</div>
          <div className="sidebar-brand-subtitle">Smart Agriculture</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id || (activeTab === 'plant-detail' && item.id === 'my-plants');

          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <div className="nav-item-left">
                <Icon size={20} />
                <span>{item.label}</span>
              </div>

              {item.badge && (
                <span className="nav-item-badge">{item.badge}</span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="grower-card">
          <div className="grower-avatar">
            {growerProfile.name ? growerProfile.name.charAt(0) : 'G'}
          </div>
          <div className="grower-info">
            <div className="grower-name" title={growerProfile.name}>{growerProfile.name}</div>
            <div className="grower-status">
              <span className="pulse-dot"></span> IoT Gateway Online
            </div>
          </div>
          <button className="btn-secondary btn-sm" onClick={logout} title="Sign Out">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
};
