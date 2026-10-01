import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { AddEditPlantModal } from './AddEditPlantModal';
import { ArrowLeft, Thermometer, Activity, Droplets, Waves, Server, Edit, Trash2, TrendingUp } from 'lucide-react';
import './Plants.css';

export const PlantDetail = () => {
  const { selectedPlantId, plants, setActiveTab, deletePlant } = useApp();
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const plant = plants.find(p => p.id === selectedPlantId) || plants[0];

  if (!plant) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '4rem' }}>
        <h2>Plant Not Found</h2>
        <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => setActiveTab('my-plants')}>
          Back to My Plants
        </button>
      </div>
    );
  }

  const renderMetricValue = (value, unit = '') => value == null
    ? <span style={{ color: 'var(--text-muted)', fontWeight: 700 }}>Waiting for data</span>
    : <span style={{ fontWeight: 800 }}>{value}{unit}</span>;

  // Growth pattern chart SVG math calculation
  const history = (plant.growthHistory || []).filter((reading) => Number.isFinite(reading.heightCm));

  const maxHeight = Math.max(...history.map(h => h.heightCm), 50);
  const points = history.map((h, index) => {
    const x = (index / (history.length - 1)) * 500 + 40;
    const y = 220 - (h.heightCm / maxHeight) * 180;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="page-container">
      <button className="btn btn-secondary btn-sm" onClick={() => setActiveTab('my-plants')} style={{ marginBottom: '1.5rem' }}>
        <ArrowLeft size={16} /> Back to My Plants
      </button>

      {/* Plant Header Card */}
      <div className="glass-card plant-detail-header-card">
        <img src={plant.image} alt={plant.name} className="plant-detail-img" />
        
        <div className="plant-detail-info">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1 className="plant-detail-name">{plant.name}</h1>
              <p className="page-subtitle">{plant.species} • {plant.location}</p>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn btn-secondary btn-sm" onClick={() => setIsEditModalOpen(true)}>
                <Edit size={16} /> Edit Plant
              </button>
              <button className="btn btn-danger btn-sm" onClick={() => deletePlant(plant.id)}>
                <Trash2 size={16} /> Delete
              </button>
            </div>
          </div>

          <div style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Overall Health:</span>
            <span className={`badge badge-${plant.status.toLowerCase().replace(' ', '-')}`}>
              {plant.status}
            </span>
          </div>
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid-4" style={{ marginBottom: '2rem' }}>
        {/* Temperature Box */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span className="form-label"><Thermometer size={18} color="var(--accent-emerald)" /> Temperature</span>
          </div>
          <div style={{ fontSize: '1.75rem' }}>
            {renderMetricValue(plant.metrics.temperature, '°C')}
          </div>
        </div>

        {/* PH Box */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span className="form-label"><Activity size={18} color="var(--accent-emerald)" /> PH</span>
          </div>
          <div style={{ fontSize: '1.75rem' }}>
            {renderMetricValue(plant.metrics.ph, '')}
          </div>
        </div>

        {/* Humidity Box */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span className="form-label"><Droplets size={18} color="var(--status-good)" /> Humidity in air</span>
          </div>
          <div style={{ fontSize: '1.75rem' }}>
            {renderMetricValue(plant.metrics.humidity, '%')}
          </div>
        </div>

        {/* Water Level Box */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span className="form-label"><Waves size={18} color="var(--status-good)" /> Water Level</span>
          </div>
          <div style={{ fontSize: '1.75rem' }}>
            {renderMetricValue(plant.metrics.waterLevel, '%')}
          </div>
        </div>
      </div>

      {/* Connectivity & Growth Pattern Grid */}
      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        {/* Connectivity with the sensors */}
        <div className="glass-card sensor-connectivity-card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Server size={22} color="var(--accent-emerald)" />
            Department server
          </h2>

          <div className="sensor-list">
            <div className="sensor-item">
              <span>Server address</span>
              <span>{plant.serverIp || 'Not configured'}</span>
            </div>
            <div className="sensor-item">
              <span>Collection</span>
              <span className={`badge ${plant.collectionStatus === 'collecting' ? 'badge-healthy' : 'badge-warning'}`}>
                {plant.collectionStatus === 'collecting' ? 'Collecting' : plant.collectionStatus || 'Not connected'}
              </span>
            </div>
          </div>
        </div>

        {/* Growth pattern Chart */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingUp size={22} color="var(--accent-emerald)" />
            Growth pattern
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Historical plant canopy height progression over telemetry intervals
          </p>

          <div className="growth-chart-container">
            {history.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem 1rem' }}>
                Growth measurements are not available from the connected server.
              </div>
            ) : (
            <svg viewBox="0 0 580 260" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
              {/* Grid Lines */}
              <line x1="40" y1="40" x2="540" y2="40" stroke="var(--border-color)" strokeDasharray="4 4" />
              <line x1="40" y1="100" x2="540" y2="100" stroke="var(--border-color)" strokeDasharray="4 4" />
              <line x1="40" y1="160" x2="540" y2="160" stroke="var(--border-color)" strokeDasharray="4 4" />
              <line x1="40" y1="220" x2="540" y2="220" stroke="var(--border-color)" />

              {/* Area Gradient fill */}
              <defs>
                <linearGradient id="growthGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--accent-emerald)" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="var(--accent-emerald)" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <polygon
                points={`40,220 ${points} 540,220`}
                fill="url(#growthGrad)"
              />

              {/* Line */}
              <polyline
                fill="none"
                stroke="var(--accent-emerald)"
                strokeWidth="4"
                strokeLinecap="round"
                points={points}
              />

              {/* Points & Labels */}
              {history.map((h, i) => {
                const x = (i / (history.length - 1)) * 500 + 40;
                const y = 220 - (h.heightCm / maxHeight) * 180;
                return (
                  <g key={i}>
                    <circle cx={x} cy={y} r="6" fill="var(--bg-card-solid)" stroke="var(--accent-emerald)" strokeWidth="3" />
                    <text x={x} y={y - 12} fill="var(--text-main)" fontSize="11" fontWeight="700" textAnchor="middle">
                      {h.heightCm} cm
                    </text>
                    <text x={x} y="242" fill="var(--text-muted)" fontSize="11" textAnchor="middle">
                      {h.day}
                    </text>
                  </g>
                );
              })}
            </svg>
            )}
          </div>
        </div>
      </div>

      <AddEditPlantModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        plantToEdit={plant}
      />
    </div>
  );
};
