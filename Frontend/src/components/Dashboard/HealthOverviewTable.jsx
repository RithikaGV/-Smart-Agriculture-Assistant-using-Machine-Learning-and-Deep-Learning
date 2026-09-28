import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Search, Thermometer, Droplets, Activity, Waves, ExternalLink } from 'lucide-react';

export const HealthOverviewTable = () => {
  const { plants, navigateToPlantDetail } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('ALL');

  const filteredPlants = plants.filter(plant => {
    const matchesSearch = plant.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          plant.species.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'ALL' || plant.status.toUpperCase() === filterStatus.toUpperCase();
    return matchesSearch && matchesFilter;
  });

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'Healthy': return 'badge-healthy';
      case 'Good': return 'badge-good';
      case 'Needs Attention': return 'badge-needs-attention';
      case 'Critical': return 'badge-critical';
      default: return 'badge-good';
    }
  };

  return (
    <div className="glass-card health-overview-section">
      <div className="table-header-controls">
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Plants Health Overview</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Real-time live telemetry metrics for pH, Humidity in air, Water Level, and Temperature.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div className="search-input-wrapper">
            <Search className="search-icon" size={16} />
            <input
              type="text"
              className="form-control"
              placeholder="Search plant name or species..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <select
            className="form-control"
            style={{ width: 'auto' }}
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="ALL">All Health Statuses</option>
            <option value="HEALTHY">Healthy</option>
            <option value="GOOD">Good</option>
            <option value="NEEDS ATTENTION">Needs Attention</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      <div className="overview-table-container">
        <table className="overview-table">
          <thead>
            <tr>
              <th>Plant Name</th>
              <th>Temperature (°C)</th>
              <th>pH Level</th>
              <th>Humidity in Air</th>
              <th>Water Level</th>
              <th>Health Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredPlants.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                  No plants found matching the selected search criteria.
                </td>
              </tr>
            ) : (
              filteredPlants.map((plant) => (
                <tr key={plant.id} onClick={() => navigateToPlantDetail(plant.id)}>
                  <td>
                    <div className="plant-cell">
                      <img src={plant.image} alt={plant.name} className="plant-thumb" />
                      <div>
                        <div className="plant-cell-name">{plant.name}</div>
                        <div className="plant-cell-species">{plant.species}</div>
                      </div>
                    </div>
                  </td>

                  <td>
                    <div className="metric-pill">
                      <Thermometer size={16} color={plant.metrics.temperature > 30 ? 'var(--status-critical)' : 'var(--accent-emerald)'} />
                      <span style={{ fontWeight: 700 }}>{plant.metrics.temperature}°C</span>
                    </div>
                  </td>

                  <td>
                    <div className="metric-pill">
                      <Activity size={16} color={plant.metrics.ph < 5.5 || plant.metrics.ph > 7.2 ? 'var(--status-warning)' : 'var(--accent-emerald)'} />
                      <span style={{ fontWeight: 700 }}>{plant.metrics.ph}</span>
                    </div>
                  </td>

                  <td>
                    <div className="metric-pill">
                      <Droplets size={16} color="var(--status-good)" />
                      <span>{plant.metrics.humidity}%</span>
                    </div>
                  </td>

                  <td>
                    <div className="metric-pill">
                      <Waves size={16} color={plant.metrics.waterLevel < 20 ? 'var(--status-critical)' : 'var(--accent-emerald)'} />
                      <span>{plant.metrics.waterLevel}%</span>
                    </div>
                  </td>

                  <td>
                    <span className={`badge ${getStatusBadgeClass(plant.status)}`}>
                      {plant.status}
                    </span>
                  </td>

                  <td>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigateToPlantDetail(plant.id);
                      }}
                      title="View Detailed Telemetry Page"
                    >
                      <span>View Details</span>
                      <ExternalLink size={14} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
