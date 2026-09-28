import React, { useState, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import { DEFAULT_PLANT_IMAGE } from '../../data/mockData';
import { X, Image as ImageIcon, Cpu, Thermometer, Activity, Droplets, Waves, Upload } from 'lucide-react';

export const AddEditPlantModal = ({ isOpen, onClose, plantToEdit }) => {
  const { addPlant, updatePlant } = useApp();

  const [name, setName] = useState('');
  const [species, setSpecies] = useState('Tomato (Solanum lycopersicum)');
  const [customSpecies, setCustomSpecies] = useState('');
  const [location, setLocation] = useState('Greenhouse Alpha - Bay 1');
  const [imageUrl, setImageUrl] = useState('');
  
  // Sensor inputs
  const [tempAddress, setTempAddress] = useState('BLE-TEMP-001X');
  const [phAddress, setPhAddress] = useState('I2C-PH-002Y');
  const [waterAddress, setWaterAddress] = useState('ADC-WTR-003Z');
  const [humidityAddress, setHumidityAddress] = useState('BLE-HUM-004W');

  // Connection toggles
  const [tempConnected, setTempConnected] = useState(true);
  const [phConnected, setPhConnected] = useState(true);
  const [waterConnected, setWaterConnected] = useState(true);
  const [humidityConnected, setHumidityConnected] = useState(true);

  useEffect(() => {
    if (plantToEdit) {
      setName(plantToEdit.name || '');
      setSpecies(plantToEdit.species || 'Tomato (Solanum lycopersicum)');
      setLocation(plantToEdit.location || 'Greenhouse Alpha - Bay 1');
      setImageUrl(plantToEdit.image || '');
      
      setTempAddress(plantToEdit.sensors?.temperature?.address || 'BLE-TEMP-001X');
      setTempConnected(plantToEdit.sensors?.temperature?.connected ?? true);
      
      setPhAddress(plantToEdit.sensors?.ph?.address || 'I2C-PH-002Y');
      setPhConnected(plantToEdit.sensors?.ph?.connected ?? true);
      
      setWaterAddress(plantToEdit.sensors?.waterLevel?.address || 'ADC-WTR-003Z');
      setWaterConnected(plantToEdit.sensors?.waterLevel?.connected ?? true);
      
      setHumidityAddress(plantToEdit.sensors?.humidity?.address || 'BLE-HUM-004W');
      setHumidityConnected(plantToEdit.sensors?.humidity?.connected ?? true);
    } else {
      setName('');
      setSpecies('Tomato (Solanum lycopersicum)');
      setLocation('Greenhouse Alpha - Bay 1');
      setImageUrl('');
      setTempConnected(true);
      setPhConnected(true);
      setWaterConnected(true);
      setHumidityConnected(true);
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

  const handleSubmit = (e) => {
    e.preventDefault();
    const finalSpecies = species === 'Custom' ? customSpecies : species;
    
    // Fallback default image if empty
    const finalImage = imageUrl.trim() !== '' ? imageUrl : DEFAULT_PLANT_IMAGE;

    const sensorPayload = {
      temperature: {
        connected: tempConnected,
        battery: tempConnected ? 95 : 0,
        address: tempAddress,
        statusText: tempConnected ? "Connected and battery level good" : "Not Connected"
      },
      ph: {
        connected: phConnected,
        battery: phConnected ? 90 : 0,
        address: phAddress,
        statusText: phConnected ? "Connected and battery level good" : "Not Connected"
      },
      waterLevel: {
        connected: waterConnected,
        battery: waterConnected ? 88 : 0,
        address: waterAddress,
        statusText: waterConnected ? "Connected and battery level good" : "Not Connected"
      },
      humidity: {
        connected: humidityConnected,
        battery: humidityConnected ? 92 : 0,
        address: humidityAddress,
        statusText: humidityConnected ? "Connected and battery level good" : "Not Connected"
      }
    };

    if (plantToEdit) {
      updatePlant(plantToEdit.id, {
        name,
        species: finalSpecies,
        location,
        image: finalImage,
        sensors: sensorPayload
      });
    } else {
      addPlant({
        name,
        species: finalSpecies,
        location,
        image: finalImage,
        sensors: sensorPayload
      });
    }
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">
            {plantToEdit ? 'Edit Plant Details' : 'Add New Plant & Connect Sensors'}
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
                  if (!name) setName(e.target.value.split(' ')[0]);
                }}
              >
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

            {/* Sensors Section */}
            <div style={{ marginTop: '0.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Cpu size={18} color="var(--accent-emerald)" />
                Sensors (It must allow user to connect to sensors)
              </h3>

              {/* Temperature Sensor */}
              <div className="form-group" style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span className="form-label"><Thermometer size={16} /> Temperature sensor</span>
                  <button
                    type="button"
                    className={`btn btn-sm ${tempConnected ? 'btn-primary' : 'btn-outline'}`}
                    onClick={() => setTempConnected(!tempConnected)}
                  >
                    {tempConnected ? '✓ Connected' : '+connect'}
                  </button>
                </div>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Address to connect (e.g. BLE-TEMP-001X)"
                  value={tempAddress}
                  onChange={(e) => setTempAddress(e.target.value)}
                />
              </div>

              {/* PH Sensor */}
              <div className="form-group" style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span className="form-label"><Activity size={16} /> PH sensor</span>
                  <button
                    type="button"
                    className={`btn btn-sm ${phConnected ? 'btn-primary' : 'btn-outline'}`}
                    onClick={() => setPhConnected(!phConnected)}
                  >
                    {phConnected ? '✓ Connected' : '+connect'}
                  </button>
                </div>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Address to connect (e.g. I2C-PH-002Y)"
                  value={phAddress}
                  onChange={(e) => setPhAddress(e.target.value)}
                />
              </div>

              {/* Water Level Sensor */}
              <div className="form-group" style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span className="form-label"><Waves size={16} /> Water level sensor</span>
                  <button
                    type="button"
                    className={`btn btn-sm ${waterConnected ? 'btn-primary' : 'btn-outline'}`}
                    onClick={() => setWaterConnected(!waterConnected)}
                  >
                    {waterConnected ? '✓ Connected' : '+connect'}
                  </button>
                </div>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Address to connect (e.g. ADC-WTR-003Z)"
                  value={waterAddress}
                  onChange={(e) => setWaterAddress(e.target.value)}
                />
              </div>

              {/* Humidity Sensor */}
              <div className="form-group" style={{ background: 'var(--bg-input)', padding: '0.85rem', borderRadius: 'var(--radius-md)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span className="form-label"><Droplets size={16} /> Humidity sensor</span>
                  <button
                    type="button"
                    className={`btn btn-sm ${humidityConnected ? 'btn-primary' : 'btn-outline'}`}
                    onClick={() => setHumidityConnected(!humidityConnected)}
                  >
                    {humidityConnected ? '✓ Connected' : '+connect'}
                  </button>
                </div>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Address to connect (e.g. BLE-HUM-004W)"
                  value={humidityAddress}
                  onChange={(e) => setHumidityAddress(e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              {plantToEdit ? 'Save Changes' : 'Add Plant'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
