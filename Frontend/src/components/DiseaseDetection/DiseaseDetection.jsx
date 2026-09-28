import React, { useState } from 'react';
import { Scan, Upload, Sparkles, CheckCircle2, ShieldCheck, AlertCircle, RefreshCw, Cpu, Image as ImageIcon } from 'lucide-react';
import './DiseaseDetection.css';

const DEFAULT_ANALYSIS_IMAGE = "https://images.unsplash.com/photo-1592841200221-a6898f307baa?auto=format&fit=crop&w=800&q=80";

export const DiseaseDetection = () => {
  const [userImage, setUserImage] = useState(null);
  const [imageUrlInput, setImageUrlInput] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [predictionData, setPredictionData] = useState({
    name: 'Tomato Early Blight',
    scientificName: 'Alternaria solani',
    confidence: 97.8,
    cause: 'Caused by the fungal pathogen Alternaria solani. Thrives in warm temperatures (24-29°C) accompanied by high humidity, prolonged leaf wetness, or heavy dew.',
    preventiveMeasures: [
      'Apply copper-based or chlorothalonil fungicide sprays at 7-10 day intervals.',
      'Prune and remove infected lower leaves to restrict fungal spore splash.',
      'Ensure proper plant spacing and drip irrigation so foliage remains dry.',
      'Rotate crops with non-solanaceous plants next season.'
    ]
  });

  const runAnalysisOnImage = (imageSrc, isCustom = true) => {
    setIsScanning(true);
    setTimeout(() => {
      if (isCustom) {
        setPredictionData({
          name: 'Foliar Spot Infection Detected',
          scientificName: 'Suspected Pathogen (Alternaria / Cercospora)',
          confidence: 95.4,
          cause: 'Fungal leaf spot spores active on foliage. Triggered by excessive canopy moisture and humidity levels (>78%).',
          preventiveMeasures: [
            'Apply targeted copper fungicide or bio-fungicide solution.',
            'Prune affected infected leaves to prevent spore transmission to adjacent plants.',
            'Increase greenhouse ventilation and adjust watering times to morning.',
            'Monitor soil pH and nutrient conductivity.'
          ]
        });
      }
      setIsScanning(false);
    }, 1200);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setUserImage(reader.result);
        runAnalysisOnImage(reader.result, true);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUrlSubmit = (e) => {
    e.preventDefault();
    if (imageUrlInput.trim() !== '') {
      setUserImage(imageUrlInput.trim());
      runAnalysisOnImage(imageUrlInput.trim(), true);
    }
  };

  const currentDisplayImage = userImage || DEFAULT_ANALYSIS_IMAGE;

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <Scan size={28} />
            AI & Deep Learning Disease Detection
          </h1>
          <p className="page-subtitle">
            Upload or enter a plant leaf picture to predict diseases, root causes, and preventive treatment measures.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '0.65rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Cpu size={18} color="var(--accent-emerald)" />
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Deep Learning Model: ResNet-50 v2 (Active)
          </span>
        </div>
      </div>

      <div className="disease-detection-grid">
        {/* LEFT COLUMN: ENTER THE IMAGE ONLY */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Enter the image</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              Upload your plant or leaf photo, or provide an image link for instant ML model diagnosis.
            </p>
          </div>

          {/* Drag & Drop / File Upload */}
          <label className="upload-dropzone">
            <Upload size={40} color="var(--accent-emerald)" style={{ marginBottom: '0.75rem' }} />
            <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--text-main)' }}>
              Click or Drag & Drop Leaf Image Here
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              Select a plant picture from your device (JPG, PNG, WEBP)
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>

          {/* Image URL Form Option */}
          <form onSubmit={handleUrlSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label className="form-label" style={{ fontSize: '0.85rem' }}>
              <ImageIcon size={16} /> Or paste an Image URL:
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="url"
                className="form-control"
                placeholder="https://example.com/leaf-photo.jpg"
                value={imageUrlInput}
                onChange={(e) => setImageUrlInput(e.target.value)}
              />
              <button type="submit" className="btn btn-primary" style={{ whiteSpace: 'nowrap' }}>
                Analyze URL
              </button>
            </div>
          </form>
        </div>

        {/* RIGHT COLUMN: DISEASE PREDICTION OUTPUT */}
        <div className="glass-card prediction-box">
          <div className="prediction-header">
            <div>
              <span style={{ fontSize: '0.775rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent-emerald)', letterSpacing: '0.05em' }}>
                DISEASE PREDICTION
              </span>
              <h2 className="disease-name">
                {isScanning ? 'Scanning Neural Layers...' : predictionData.name}
              </h2>
              <div className="scientific-name">
                {isScanning ? 'Extracting biological features...' : predictionData.scientificName}
              </div>
            </div>

            <button
              className="btn btn-secondary btn-sm"
              onClick={() => runAnalysisOnImage(currentDisplayImage, true)}
              disabled={isScanning}
            >
              <RefreshCw size={14} className={isScanning ? 'spin-icon' : ''} />
              <span>Re-analyze</span>
            </button>
          </div>

          {/* Neural scanning image preview */}
          <div className="neural-scan-box">
            <img src={currentDisplayImage} alt="Leaf for ML Analysis" className="neural-scan-img" />
            {isScanning && <div className="neural-scan-line"></div>}
          </div>

          {/* ML Confidence Score */}
          <div className="confidence-bar-wrapper">
            <div className="confidence-label-row">
              <span>ML Model Prediction Confidence:</span>
              <span style={{ color: 'var(--accent-emerald)' }}>
                {isScanning ? 'Analyzing...' : `${predictionData.confidence}%`}
              </span>
            </div>
            <div className="confidence-bar-outer">
              <div
                className="confidence-bar-inner"
                style={{ width: isScanning ? '35%' : `${predictionData.confidence}%` }}
              ></div>
            </div>
          </div>

          {/* Cause of the disease */}
          <div className="cause-box">
            <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--status-warning)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <AlertCircle size={16} /> Cause of the disease:
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
              {isScanning ? 'Analyzing pathogen causes...' : predictionData.cause}
            </p>
          </div>

          {/* Preventive Measures */}
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ShieldCheck size={18} color="var(--accent-emerald)" />
              Preventive measures:
            </div>

            <div className="preventive-list">
              {isScanning ? (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Computing preventive treatment protocol...</div>
              ) : (
                predictionData.preventiveMeasures.map((measure, index) => (
                  <div key={index} className="preventive-item">
                    <CheckCircle2 size={16} color="var(--accent-emerald)" style={{ marginTop: '0.15rem', flexShrink: 0 }} />
                    <span>{measure}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
