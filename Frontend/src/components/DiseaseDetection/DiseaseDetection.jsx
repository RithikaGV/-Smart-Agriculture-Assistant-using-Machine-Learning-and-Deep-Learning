import React, { useState } from 'react';
import { Scan, Upload, CheckCircle2, ShieldCheck, AlertCircle, RefreshCw, Cpu, Image as ImageIcon } from 'lucide-react';
import { api } from '../../api/client';
import './DiseaseDetection.css';

const DEFAULT_ANALYSIS_IMAGE = "https://images.unsplash.com/photo-1592841200221-a6898f307baa?auto=format&fit=crop&w=800&q=80";

export const DiseaseDetection = () => {
  const [userImage, setUserImage] = useState(null);
  const [imageUrlInput, setImageUrlInput] = useState('');
  const [analysisInput, setAnalysisInput] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [predictionData, setPredictionData] = useState(null);

  const runAnalysis = async (input, requestPrediction) => {
    setAnalysisInput(input);
    setIsScanning(true);
    setErrorMessage('');
    try {
      const prediction = await requestPrediction();
      setPredictionData({
        name: prediction.name,
        scientificName: prediction.scientificName,
        confidence: prediction.confidence,
        cause: prediction.cause,
        preventiveMeasures: prediction.preventiveMeasures,
      });
    } catch (error) {
      setPredictionData(null);
      setErrorMessage(error.message || 'Disease prediction failed. Please try another image.');
    } finally {
      setIsScanning(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageUrlInput('');
      const reader = new FileReader();
      reader.onloadend = () => {
        setUserImage(reader.result);
      };
      reader.readAsDataURL(file);
      await runAnalysis({ type: 'file', value: file }, () => api.predictDisease(file));
    }
  };

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    const imageUrl = imageUrlInput.trim();
    if (!imageUrl) return;

    setUserImage(imageUrl);
    await runAnalysis({ type: 'url', value: imageUrl }, () => api.predictDiseaseJson(imageUrl));
  };

  const reanalyze = () => {
    if (!analysisInput) return;
    const requestPrediction = analysisInput.type === 'file'
      ? () => api.predictDisease(analysisInput.value)
      : () => api.predictDiseaseJson(analysisInput.value);
    runAnalysis(analysisInput, requestPrediction);
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
            Upload a plant leaf picture or enter its image URL to predict diseases, root causes, and preventive treatment measures.
          </p>
        </div>

        <div className="glass-card" style={{ padding: '0.65rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Cpu size={18} color="var(--accent-emerald)" />
          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Botanical Vision Classifier
          </span>
        </div>
      </div>

      <div className="disease-detection-grid">
        {/* LEFT COLUMN: ENTER THE IMAGE ONLY */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Enter the image</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              Upload a plant or leaf photo, or provide a direct image URL for model diagnosis.
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
              disabled={isScanning}
              style={{ display: 'none' }}
            />
          </label>

          <form onSubmit={handleUrlSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label className="form-label" style={{ fontSize: '0.85rem' }}>
              <ImageIcon size={16} /> Or paste an image URL:
            </label>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <input
                type="url"
                className="form-control"
                placeholder="https://example.com/leaf-photo.jpg"
                value={imageUrlInput}
                onChange={(e) => setImageUrlInput(e.target.value)}
                disabled={isScanning}
              />
              <button type="submit" className="btn btn-primary" style={{ whiteSpace: 'nowrap' }} disabled={isScanning || !imageUrlInput.trim()}>
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
                {isScanning ? 'Analyzing leaf image...' : predictionData?.name || 'Awaiting leaf image'}
              </h2>
              <div className="scientific-name">
                {isScanning ? 'Extracting botanical features...' : predictionData?.scientificName || 'Prediction details will appear here'}
              </div>
            </div>

            <button
              className="btn btn-secondary btn-sm"
              onClick={reanalyze}
              disabled={isScanning || !analysisInput}
            >
              <RefreshCw size={14} className={isScanning ? 'spin-icon' : ''} />
              <span>Re-analyze</span>
            </button>
          </div>

          {errorMessage && <div role="alert" className="alert-description">{errorMessage}</div>}

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
                {isScanning ? 'Analyzing...' : predictionData ? `${predictionData.confidence}%` : '--'}
              </span>
            </div>
            <div className="confidence-bar-outer">
              <div
                className="confidence-bar-inner"
                style={{ width: isScanning ? '35%' : `${predictionData?.confidence || 0}%` }}
              ></div>
            </div>
          </div>

          {/* Cause of the disease */}
          <div className="cause-box">
            <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--status-warning)', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <AlertCircle size={16} /> Cause of the disease:
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-main)', lineHeight: 1.5 }}>
              {isScanning ? 'Analyzing pathogen causes...' : predictionData?.cause || 'Upload a leaf image to see its predicted cause.'}
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
              ) : predictionData ? (
                predictionData.preventiveMeasures.map((measure, index) => (
                  <div key={index} className="preventive-item">
                    <CheckCircle2 size={16} color="var(--accent-emerald)" style={{ marginTop: '0.15rem', flexShrink: 0 }} />
                    <span>{measure}</span>
                  </div>
                ))
              ) : (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Treatment measures will appear after analysis.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
