# Hydroponic Smart Plant System — Machine Learning Models Documentation

Welcome to the Machine Learning documentation for the **Hydroponic Smart Plant System**. This document provides an in-depth explanation of both ML models developed for this project:

1. **Model 1: Spinach Plant Health & Corrective Remedy Suggester** (Sensor-based telemetry classification and automated corrective action planning)
2. **Model 2: Plant Leaf Disease Detection Model** (Agronomic botanical vision classifier trained on leaf disease images)

---

## 📋 System Architecture Overview

```
                               ┌─────────────────────────────────────────────────────────────┐
                               │               Hydroponic Smart Plant System                 │
                               └──────────────────────────────┬──────────────────────────────┘
                                                              │
                     ┌────────────────────────────────────────┴────────────────────────────────────────┐
                     ▼                                                                                 ▼
     ┌────────────────────────────────┐                                                ┌────────────────────────────────┐
     │            MODEL 1             │                                                │            MODEL 2             │
     │   Spinach Health & Remedies    │                                                │ Image-Based Disease Predictor  │
     └───────────────┬────────────────┘                                                └───────────────┬────────────────┘
                     │                                                                                 │
       Telemetry: pH, Humidity, Temp,                                                   Input: Uploaded Leaf Photo
             Water Level, TDS                                                                          │
                     │                                                                                 │
                     ▼                                                                                 ▼
     ┌────────────────────────────────┐                                                ┌────────────────────────────────┐
     │     Random Forest Classifier   │                                                │   ExtraTrees Botanical Vision  │
     │     (100% Validation Acc.)     │                                                │   Classifier (90.5% Accuracy)  │
     └───────────────┬────────────────┘                                                └───────────────┬────────────────┘
                     │                                                                                 │
                     ▼                                                                                 ▼
         Output Diagnosis & Actions:                                                       Output Disease Diagnosis:
     • Status: Healthy / Unhealthy                                                     • Predicted: Spinach - Downy Mildew
     • Health Score: 0 – 100%                                                          • Confidence: 91.0%
     • Identified Stress Factors                                                       • Severity: Severe / Moderate / Mild
     • Step-by-Step Remedial Actions                                                   • Actionable Bio & Chemical Remedies
```

---

## 🥬 Model 1: Spinach Plant Health & Corrective Remedy Suggester

### 1. Purpose & Dataset
- **Objective**: Analyze real-time IoT sensor telemetry from the hydroponic nutrient reservoir and grow environment to classify the spinach plant as **Healthy** or **Unhealthy**. If unhealthy, automatically generate **precise, step-by-step agronomic corrective measures** to restore optimal conditions.
- **Dataset**: Trained on the faculty spinach sensor dataset (`sensor_data.csv`, 4,138 telemetry readings).
- **Features Used**:
  1. `pH`: Solution acidity / alkalinity (Spinach optimal: 5.8 – 6.5)
  2. `humidity`: Ambient relative humidity % (Spinach optimal: 50.0% – 70.0%)
  3. `temperature`: Nutrient solution / ambient temperature in °C (Spinach optimal: 18.0°C – 25.0°C)
  4. `water_level`: Reservoir volume buffer % (Safe threshold: ≥ 40.0%)
  5. `tds_ppm`: Total Dissolved Solids / nutrient ionic strength (Spinach optimal: 550 – 900 ppm)

### 2. Model Performance
- **Algorithm**: Balanced `RandomForestClassifier` (120 estimators, depth 12)
- **Validation Accuracy**: **100.00%**
- **Precision / Recall / F1**: **1.00 / 1.00 / 1.00**
- **Feature Importance**:
  - `pH`: 38.03%
  - `temperature`: 34.15%
  - `tds_ppm`: 20.12%
  - `water_level`: 6.54%
  - `humidity`: 1.16%

### 3. How to Run & Test Model 1
Run inference directly from the command line:

```bash
# Test 1: Optimal Healthy Conditions
python ml_models/predict_spinach_health.py --ph 6.2 --humidity 60 --temp 22 --water 85 --tds 700

# Test 2: Unhealthy Conditions (Alkaline pH, Dry Air, Hot Solution, Low Water & TDS)
python ml_models/predict_spinach_health.py --ph 7.8 --humidity 42 --temp 29 --water 30 --tds 480
```

#### Example Output:
```
======================================================================
🌱 SPINACH HEALTH & CORRECTIVE REMEDY PREDICTION REPORT
======================================================================
Health Status : ⚠️ Unhealthy
Confidence    : 87.5%
Health Score  : 40.0%
----------------------------------------------------------------------
Input Telemetry Readings:
  • temperature   : 29.0 °C
  • pH            : 7.80
  • humidity      : 42.0%
  • water_level   : 30.0%
  • tds_ppm       : 480.0 ppm
----------------------------------------------------------------------
Detected Stress Factor(s):
  🚨 Alkaline Solution (pH 7.80 > 6.50): Causes rapid Iron and Micronutrient lockout, triggering leaf yellowing/chlorosis.
  🚨 Low Humidity (42.0% < 50%): High vapor pressure deficit causes severe transpiration stress and leaf tip burn.
  🚨 Elevated Temperature (29.0°C > 25.0°C): Warm solution drops dissolved oxygen (DO) levels, risking Pythium root rot.
  🚨 Low Reservoir Water Level (30.0% < 40%): Risk of pump dry-run and rapid nutrient salt concentration.
  🚨 Nutrient Deficiency (TDS 480.0 ppm < 550 ppm): Insufficient ionic nitrogen, potassium, and magnesium for vegetative spinach.
----------------------------------------------------------------------
Recommended Action Steps & Remedies:
  [1] Step 1 (pH Remedy): Add 3–5 mL of food-grade pH Down (dilute phosphoric/nitric acid buffer). Mix thoroughly. If leaf chlorosis has already appeared, administer foliar chelated iron (Fe-EDDHA 0.05%).
  [2] Step 2 (Humidity Remedy): Engage ultrasonic humidifier or misting nozzles for 2 minutes every 15 minutes. Adjust intake/exhaust air damper to bring grow room relative humidity to 55–65%.
  [3] Step 3 (Temperature Remedy): Activate inline nutrient reservoir chiller to maintain 18–22°C root zone temperature. Increase air pump flow rate to oxygenate nutrient reservoir.
  [4] Step 4 (Water Level Remedy): Top up nutrient tank immediately with fresh dechlorinated / reverse-osmosis water until level reaches at least 80% capacity.
  [5] Step 5 (Nutrient Remedy): Dose balanced Hydroponic Fertilizer Part A and Part B (1:1 ratio) until TDS reads 650–800 ppm.
======================================================================
```

---

## 🍃 Model 2: Image-Based Plant Disease Detection Model

### 1. Purpose & Dataset
- **Objective**: Accept an image of a plant leaf uploaded by a user, isolate the foliar tissue, extract 39 botanical computer vision metrics, classify the exact disease, estimate infection severity, and prescribe targeted biological and environmental treatments.
- **Dataset**: Trained on the real plant disease image dataset located in `Downloads\ML_dataset_Disease_detection` (36,961 total images across 9 crops).
- **Core Disease Classes Trained**:
  1. `Spinach - Anthracnose` (*Colletotrichum dematium*)
  2. `Spinach - Bacterial Spot` (*Pseudomonas syringae*)
  3. `Spinach - Downy Mildew` (*Peronospora effusa*)
  4. `Spinach - Healthy Leaf` (Optimal vegetative foliage)
  5. `Spinach - Pest Damage` (Thrips, aphids, chewed margins)
  6. `Cucumber - Powdery Mildew` (*Podosphaera xanthii*)
  7. `Cucumber - Downy Mildew` (*Pseudoperonospora cubensis*)
  8. `Basil - Fusarium Wilt` (*Fusarium oxysporum*)
  9. `Tomato - Early Blight` (*Alternaria solani*)

### 2. Botanical Computer Vision Features
The model extracts **39 computer vision features** designed specifically for plant pathology without requiring GPU or deep learning overhead:
1. **Color Moments**: Mean and standard deviation across R, G, B, Hue, Saturation, and Brightness.
2. **Agronomic Botanical Indices**:
   - `ExG` (Excess Green Index): $2G - R - B$
   - `ExR` (Excess Red Index): $1.4R - G$
   - `VARI` (Visible Atmospherically Resistant Index): $(G - R) / (G + R - B)$
   - `NDYI` (Normalized Difference Yellowness Index): $(G - B) / (G + B)$
3. **Pathology Lesion Signatures**:
   - White fungal powdery cluster coverage $(V > 0.65, S < 0.40)$
   - Dark necrotic margin ratio $(R > G, V < 0.35)$
   - Tan sunken anthracnose ratio
   - Chlorotic halo density $(R > 0.40, G > 0.40, B < 0.28)$
4. **Spatial Gradients & Texture**:
   - Horizontal and vertical spatial edge variance across color channels
   - Normalized Shannon Entropy of the Hue histogram

### 3. Model Performance
- **Algorithm**: `StandardScaler` + `ExtraTreesClassifier` (180 estimators, depth 18)
- **Validation Accuracy**: **90.48%**
- **Validation Metrics**:
  - Tomato Early Blight: Precision 1.00, Recall 1.00, F1 1.00
  - Cucumber Powdery Mildew: Precision 1.00, Recall 1.00, F1 1.00
  - Cucumber Downy Mildew: Precision 1.00, Recall 1.00, F1 1.00
  - Basil Fusarium Wilt: Precision 1.00, Recall 0.95, F1 0.98
  - Spinach Anthracnose: Precision 0.78, Recall 1.00, F1 0.88
  - Spinach Downy Mildew: Precision 1.00, Recall 0.79, F1 0.88
  - Spinach Healthy Leaf: Precision 0.90, Recall 0.79, F1 0.84
  - Spinach Pest Damage: Precision 0.75, Recall 0.88, F1 0.81

### 4. How to Run & Test Model 2
Run inference on any leaf image:

```bash
# Test on a Downy Mildew Leaf
python ml_models/predict_leaf.py "C:\Users\NAVEENAMS\Downloads\ML_dataset_Disease_detection\ML_dataset_Disease_detection\Spinach\Downy-Mildew(240)\Downy-Mildew (1).jpg"

# Test on a Healthy Leaf
python ml_models/predict_leaf.py "C:\Users\NAVEENAMS\Downloads\ML_dataset_Disease_detection\ML_dataset_Disease_detection\Spinach\Healthy-Leaf(1399)\Healthy-Leaf (1).jpg"
```

#### Example Output:
```
========================================================================
🌿 MODEL 2: PLANT LEAF DISEASE PREDICTION REPORT
========================================================================
Uploaded Image: Downy-Mildew (1).jpg
       ↓
AI Botanical Vision Classifier
       ↓
Prediction    : 🚨 Spinach - Downy Mildew — 91.0%
Severity Level: Severe
------------------------------------------------------------------------
Causal Agent  : Oomycete pathogen (*Peronospora effusa*) flourishing in high humidity (>75%) and cool temperatures.
Symptoms      : Irregular chlorotic yellow patches on upper leaf surface with purplish-gray mildew on underside.
------------------------------------------------------------------------
Corrective Measures & Actionable Treatment:
  [1] Immediately lower grow room relative humidity to 50–60% using dehumidifiers and exhaust fans.
  [2] Apply potassium phosphite (mono- and dipotassium salts of phosphorous acid) or bio-fungicide.
  [3] Widen plant spacing in hydroponic raft/channels to maximize horizontal airflow.
  [4] Avoid reservoir water temperatures dropping below 17°C during vegetative growth.
------------------------------------------------------------------------
Botanical Vision Indices:
  • excess_green_index    : 0.162
  • chlorosis_index_ndyi  : 0.177
  • lesion_density        : 78.1%
  • texture_gradient      : 0.03
========================================================================
```

---

## 🌐 FastAPI REST Integration

Both models are integrated into the FastAPI backend (`backend/main.py`):

### 1. Check Models Health
- **Endpoint**: `GET /api/models/status`
- **Response**:
```json
{
  "status": "ready",
  "model1_spinach_health_remedy": "loaded",
  "model2_image_disease_prediction": "loaded"
}
```

### 2. Predict Spinach Health & Remedies (Model 1)
- **Endpoint**: `POST /api/models/spinach-health`
- **Request Body**:
```json
{
  "temp": 29.5,
  "ph": 7.8,
  "humidity": 41.0,
  "water": 30.0,
  "tds": 480.0
}
```
- **Response**:
```json
{
  "status": "success",
  "result": {
    "health_status": "Unhealthy",
    "confidence": "87.5%",
    "health_score": "40.0%",
    "stress_factors": [
      "Alkaline Solution (pH 7.80 > 6.50)...",
      "Low Humidity (41.0% < 50%)...",
      "Elevated Temperature (29.5°C > 25.0°C)..."
    ],
    "remedy_measures": [
      "Step 1 (pH Remedy): Add 3–5 mL of food-grade pH Down...",
      "Step 2 (Humidity Remedy): Engage ultrasonic humidifier...",
      "Step 3 (Temperature Remedy): Activate inline reservoir chiller..."
    ]
  }
}
```

### 3. Predict Leaf Disease (Model 2)
- **Endpoint**: `POST /api/models/disease-prediction`
- **Request Body**:
```json
{
  "image_path": "C:\\path\\to\\leaf.jpg"
}
```
*(Also supports `image_base64` for web browser drag-and-drop).*
- **Response**:
```json
{
  "status": "success",
  "result": {
    "crop": "Spinach",
    "disease": "Downy Mildew",
    "confidence": "91.0%",
    "severity": "Severe",
    "treatment_recommendation": "Immediately lower grow room relative humidity to 50–60%..."
  }
}
```

---

## 📁 Artifacts & Files Included

| File | Description |
|------|-------------|
| `ml_models/model1_spinach_health_remedy.py` | Training & inference code for Model 1 (Spinach Health & Remedies) |
| `ml_models/predict_spinach_health.py` | CLI test tool for Model 1 |
| `ml_models/spinach_health_remedy_model.joblib` | Serialized joblib artifact for Model 1 |
| `ml_models/spinach_health_remedy_model.pkl` | Serialized pickle artifact for Model 1 |
| `ml_models/model2_disease_prediction.py` | Training & inference code for Model 2 (Image Disease Classifier) |
| `ml_models/predict_leaf.py` | CLI test tool for Model 2 |
| `ml_models/model2_disease_prediction.joblib` | Serialized joblib artifact for Model 2 |
| `ml_models/model2_disease_prediction.pkl` | Serialized pickle artifact for Model 2 |
| `backend/main.py` | FastAPI application serving REST endpoints and WebSockets |
| `test_api_endpoints.py` | Automated test suite verifying both models and API endpoints |
| `README_ML_MODELS.md` | Complete project documentation |
