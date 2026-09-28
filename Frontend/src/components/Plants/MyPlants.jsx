import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { PlantCard } from './PlantCard';
import { AddEditPlantModal } from './AddEditPlantModal';
import { Sprout, Plus } from 'lucide-react';

export const MyPlants = () => {
  const { plants } = useApp();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPlant, setEditingPlant] = useState(null);

  const handleOpenAddModal = () => {
    setEditingPlant(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (plant) => {
    setEditingPlant(plant);
    setIsModalOpen(true);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <Sprout size={28} />
            My Connected Plants
          </h1>
          <p className="page-subtitle">
            Manage your crop varieties, monitoring telemetry boxes, and connected IoT sensors.
          </p>
        </div>

        <button className="btn btn-primary" onClick={handleOpenAddModal}>
          <Plus size={18} />
          <span>Add More Plants</span>
        </button>
      </div>

      <div className="plants-grid">
        {plants.map((plant) => (
          <PlantCard
            key={plant.id}
            plant={plant}
            onEdit={handleOpenEditModal}
          />
        ))}
      </div>

      <AddEditPlantModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        plantToEdit={editingPlant}
      />
    </div>
  );
};
