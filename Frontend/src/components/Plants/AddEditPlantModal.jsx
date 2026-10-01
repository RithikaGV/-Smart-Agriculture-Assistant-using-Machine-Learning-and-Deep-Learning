import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { DEFAULT_PLANT_IMAGE } from '../../data/mockData';
import { X, Image as ImageIcon, Server, Upload } from 'lucide-react';

export const AddEditPlantModal = ({ isOpen, onClose, plantToEdit }) => {
  const { addPlant, updatePlant } = useApp();

  const [name, setName] = useState('');
  const [species, setSpecies] = useState('');
  const [customSpecies, setCustomSpecies] = useState('');
  const [location, setLocation] = useState('Greenhouse Alpha - Bay 1');
  const [imageUrl, setImageUrl] = useState('');
  
  const [serverIp, setServerIp] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (plantToEdit) {
      setName(plantToEdit.name || '');
      setSpecies(plantToEdit.species || '');
      setLocation(plantToEdit.location || 'Greenhouse Alpha - Bay 1');
      setImageUrl(plantToEdit.image || '');
    } else {
      setName('');
      setSpecies('');
      setLocation('Greenhouse Alpha - Bay 1');
      setImageUrl('');
      setServerIp('');
    }
  }, [plantToEdit, isOpen]);

  if (!isOpen) return null;

  const handleImageFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImageUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const finalSpecies = species === 'Custom' ? customSpecies : species;
    const finalImage = imageUrl.trim() !== '' ? imageUrl : DEFAULT_PLANT_IMAGE;
    setIsSaving(true);
    try {
      if (plantToEdit) {
        await updatePlant(plantToEdit.id, {
          name,
          species: finalSpecies,
          location,
          image: finalImage,
        });
      } else {
        const created = await addPlant({
          name,
          species: finalSpecies,
          location,
          image: finalImage,
          server_ip: serverIp.trim(),
        });
        if (!created) return;
      }
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">
            {plantToEdit ? 'Edit Plant Details' : 'Add Plant & Connect Department Server'}
          </h2>
          <button className="btn-secondary btn-sm" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {/* Plant Dropdown selection */}
            <div className="form-group">
              <label className="form-label">
                Name of the plant (From the drop down menu provided)
              </label>
              <select
                className="form-control"
                value={species}
                onChange={(e) => {
                  setSpecies(e.target.value);
                  if (!name && e.target.value !== 'Custom') setName(e.target.value.split(' ')[0]);
                }}
                required
              >
                <option value="" disabled>Select plant species</option>
                <option value="Tomato (Solanum lycopersicum)">Tomato (Solanum lycopersicum)</option>
                <option value="Bell Pepper (Capsicum annuum)">Bell Pepper (Capsicum annuum)</option>
                <option value="Lettuce (Lactuca sativa)">Butterhead Lettuce (Lactuca sativa)</option>
                <option value="Strawberry (Fragaria vesca)">Strawberry (Fragaria vesca)</option>
                <option value="Corn (Zea mays)">Corn (Zea mays)</option>
                <option value="Potato (Solanum tuberosum)">Potato (Solanum tuberosum)</option>
                <option value="Apple (Malus domestica)">Apple Tree (Malus domestica)</option>
                <option value="Custom">Other Custom Species</option>
              </select>
            </div>

            {species === 'Custom' && (
              <div className="form-group">
                <label className="form-label">Enter Custom Plant Name</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. Hydroponic Spinach"
                  value={customSpecies}
                  onChange={(e) => setCustomSpecies(e.target.value)}
                  required
                />
              </div>
            )}

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Plant Identifier Name</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. Bay 2 Hydroponics"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Location / Bed</label>
                <input
                  type="text"
                  className="form-control"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Plant Image Upload / Link */}
            <div className="form-group">
              <label className="form-label">
                <ImageIcon size={16} /> Plant Image (Insert custom image or leave blank for default)
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <input
                  type="url"
                  className="form-control"
                  placeholder="Insert image URL (https://...)"
                  value={imageUrl}
                  onChange={(e) => setImageUrl(e.target.value)}
                />
                <label className="btn btn-secondary" style={{ cursor: 'pointer', whiteSpace: 'nowrap' }}>
                  <Upload size={16} /> Upload
                  <input type="file" accept="image/*" onChange={handleImageFileChange} style={{ display: 'none' }} />
                </label>
              </div>

              <div className="image-preview-box">
                <img
                  src={imageUrl.trim() !== '' ? imageUrl : DEFAULT_PLANT_IMAGE}
                  alt="Plant preview"
                  onError={(e) => { e.target.src = DEFAULT_PLANT_IMAGE; }}
                />
                <div style={{
                  position: 'absolute',
                  bottom: '6px',
                  right: '6px',
                  background: 'rgba(0,0,0,0.65)',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  color: '#fff'
                }}>
                  {imageUrl.trim() !== '' ? 'Custom Image' : 'Default Visual Image'}
                </div>
              </div>
            </div>

            {!plantToEdit && (
              <div className="form-group" style={{ paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
                <label className="form-label" htmlFor="department-server-ip">
                  <Server size={16} /> Department Server IP Address
                </label>
                <input
                  id="department-server-ip"
                  type="text"
                  className="form-control"
                  placeholder="192.168.100.131 or http://192.168.100.131:5000/api/data"
                  value={serverIp}
                  onChange={(e) => setServerIp(e.target.value)}
                  autoComplete="url"
                  required
                />
                <small style={{ color: 'var(--text-muted)' }}>
                  A bare IP uses port 5000 and the /api/data endpoint. Collection starts when the plant is added.
                </small>
              </div>
            )}
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={isSaving}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSaving}>
              {isSaving ? 'Saving...' : plantToEdit ? 'Save Changes' : 'Add Plant & Start Collection'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
