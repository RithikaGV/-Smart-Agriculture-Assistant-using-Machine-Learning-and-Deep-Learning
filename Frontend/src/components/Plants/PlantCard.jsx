import React from 'react';
import { useApp } from '../../context/AppContext';
import { Thermometer, Activity, Droplets, Waves, Edit, Trash2, ChevronRight } from 'lucide-react';

export const PlantCard = ({ plant, onEdit }) => {
  const { navigateToPlantDetail, deletePlant } = useApp();

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
    <div className="glass-card plant-card" onClick={() => navigateToPlantDetail(plant.id)}>
      <div className="plant-card-image-container">
        <img src={plant.image} alt={plant.name} className="plant-card-img" />
        <div className="plant-card-badge-top">
          <span className={`badge ${getStatusBadgeClass(plant.status)}`}>
            {plant.status}
          </span>
        </div>
      </div>

      <div className="plant-card-body">
        <div>
          <h3 className="plant-card-title">{plant.name}</h3>
          <p className="plant-card-species">{plant.species} • {plant.location}</p>
        </div>

        <div className="plant-card-metrics-row">
          <div className="mini-metric">
            <span className="mini-metric-value">{plant.metrics.temperature}°C</span>
            <span className="mini-metric-label">Temp</span>
          </div>

          <div className="mini-metric">
            <span className="mini-metric-value">{plant.metrics.ph}</span>
            <span className="mini-metric-label">pH</span>
          </div>

          <div className="mini-metric">
            <span className="mini-metric-value">{plant.metrics.humidity}%</span>
            <span className="mini-metric-label">Humidity</span>
          </div>

          <div className="mini-metric">
            <span className="mini-metric-value">{plant.metrics.waterLevel}%</span>
            <span className="mini-metric-label">Water</span>
          </div>
        </div>
      </div>

      <div className="plant-card-footer">
        <div className="plant-card-actions">
          <button
            className="btn btn-secondary btn-sm"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(plant);
            }}
            title="Edit Plant Details"
          >
            <Edit size={13} />
            <span>Edit</span>
          </button>

          <button
            className="btn btn-danger btn-sm"
            onClick={(e) => {
              e.stopPropagation();
              if (window.confirm(`Are you sure you want to remove "${plant.name}"?`)) {
                deletePlant(plant.id);
              }
            }}
            title="Delete Plant"
          >
            <Trash2 size={13} />
            <span>Delete</span>
          </button>

          <button
            className="btn btn-outline btn-sm"
            onClick={(e) => {
              e.stopPropagation();
              navigateToPlantDetail(plant.id);
            }}
            title="View Plant Telemetry Details"
          >
            <span>Details</span>
            <ChevronRight size={13} />
          </button>
        </div>
      </div>
    </div>
  );
};
