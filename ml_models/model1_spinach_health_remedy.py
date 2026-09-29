"""
=============================================================================
MODEL 1: Spinach Plant Health & Corrective Remedy Prediction Model
=============================================================================
Dataset: Faculty Spinach Dataset (sensor_data.csv / ZIP archive)
Target:
  1. Identify whether the Spinach plant is Healthy or Unhealthy based on
     sensor telemetry features (pH, humidity, temperature, water level, TDS).
  2. If the plant is Unhealthy, provide intelligent, actionable agronomic
     remedy steps to restore optimal plant health.
=============================================================================
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import joblib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent
ML_MODELS_DIR = BASE_DIR / "ml_models"

MODEL_JOBLIB_PATH = ML_MODELS_DIR / "spinach_health_remedy_model.joblib"
MODEL_PKL_PATH = ML_MODELS_DIR / "spinach_health_remedy_model.pkl"

# Agronomic optimal parameter thresholds for Hydroponic Spinach (Spinacia oleracea)
OPTIMAL_RANGES = {
    "pH": (5.8, 6.5),             # Spinach optimal: 5.8 - 6.5
    "humidity": (50.0, 70.0),      # Optimal relative humidity: 50% - 70%
    "temperature": (18.0, 25.0),   # Optimal ambient / water temp: 18°C - 25°C
    "water_level": (40.0, 100.0),  # Safe reservoir volume: >= 40%
    "tds_ppm": (550.0, 900.0)      # Optimal EC/TDS: 550 - 900 ppm
}


def load_spinach_dataset(dataset_path: str = None) -> pd.DataFrame:
    """
    Loads faculty spinach sensor dataset (sensor_data.csv or hydroponic dataset).
    Maps columns to standard features: temperature, pH, humidity, water_level, tds_ppm.
    """
    target_csv = None
    if dataset_path and os.path.exists(dataset_path):
        target_csv = Path(dataset_path)

    if not target_csv:
        search_paths = [
            Path.home() / "Downloads" / "sensor_data.csv",
            Path(r"C:\Users\NAVEENAMS\Downloads\sensor_data.csv"),
            BASE_DIR / "hydroponic_5_dataset.csv",
            BASE_DIR / "spinach_hydroponic_processed_dataset.csv"
        ]
        for p in search_paths:
            if p.exists():
                target_csv = p
                break

    if not target_csv:
        raise FileNotFoundError("Faculty spinach sensor dataset not found in Downloads or workspace!")

    print(f"[Model 1] Ingesting spinach dataset from: {target_csv}")

    # Check if raw 14-column IoT logging format without headers
    df_raw = pd.read_csv(target_csv, nrows=5)
    if len(df_raw.columns) == 14 and pd.api.types.is_numeric_dtype(df_raw.iloc[:, 1]):
        df_full = pd.read_csv(target_csv, header=None)
        # Column mapping from raw IoT telemetry:
        # Col 4: temperature, Col 7: pH, Col 1: humidity, Col 13: water level flag, Col 9: TDS
        df = pd.DataFrame({
            "temperature": pd.to_numeric(df_full[4], errors="coerce"),
            "pH": pd.to_numeric(df_full[7], errors="coerce"),
            "humidity": pd.to_numeric(df_full[1], errors="coerce"),
            "water_level": np.where(df_full[13] == True, 85.0, 25.0),
            "tds_ppm": pd.to_numeric(df_full[9], errors="coerce")
        }).dropna()
    else:
        df_full = pd.read_csv(target_csv)
        cols_lower = {c.lower(): c for c in df_full.columns}
        temp_col = cols_lower.get("temperature") or cols_lower.get("dht_temp") or cols_lower.get("temp")
        ph_col = cols_lower.get("ph") or cols_lower.get("ph_val")
        hum_col = cols_lower.get("humidity") or cols_lower.get("dht_humidity") or cols_lower.get("hum")
        wl_col = cols_lower.get("water_level") or cols_lower.get("water_level_pct") or cols_lower.get("waterlevel")
        tds_col = cols_lower.get("tds_ppm") or cols_lower.get("tds") or cols_lower.get("ec_ppm")

        df = pd.DataFrame({
            "temperature": pd.to_numeric(df_full[temp_col], errors="coerce"),
            "pH": pd.to_numeric(df_full[ph_col], errors="coerce"),
            "humidity": pd.to_numeric(df_full[hum_col], errors="coerce"),
            "water_level": pd.to_numeric(df_full[wl_col], errors="coerce"),
            "tds_ppm": pd.to_numeric(df_full[tds_col], errors="coerce")
        }).dropna()

    # Ground-truth agronomic labeling for Spinach Health
    # If all vital parameters within safe range -> Healthy, else -> Unhealthy
    is_healthy = (
        (df["pH"].between(5.7, 6.6)) &
        (df["humidity"].between(48.0, 72.0)) &
        (df["temperature"].between(17.5, 25.5)) &
        (df["water_level"] >= 40.0) &
        (df["tds_ppm"].between(500.0, 950.0))
    )
    df["health_status"] = np.where(is_healthy, "Healthy", "Unhealthy")

    # If the raw dataset happens to have an extreme bias (e.g. all rows recorded in warm room),
    # augment with calibrated healthy spinach baseline rows to ensure strong balanced learning:
    healthy_count = (df["health_status"] == "Healthy").sum()
    unhealthy_count = (df["health_status"] == "Unhealthy").sum()
    print(f"[Model 1] Extracted {len(df)} telemetry rows. Healthy: {healthy_count}, Unhealthy: {unhealthy_count}")

    if healthy_count < 400:
        print("[Model 1] Augmenting optimal spinach healthy operating points for balanced training...")
        np.random.seed(42)
        n_healthy = 1200
        aug_healthy = pd.DataFrame({
            "temperature": np.random.uniform(18.5, 24.5, n_healthy),
            "pH": np.random.uniform(5.85, 6.45, n_healthy),
            "humidity": np.random.uniform(52.0, 68.0, n_healthy),
            "water_level": np.random.uniform(50.0, 95.0, n_healthy),
            "tds_ppm": np.random.uniform(580.0, 880.0, n_healthy),
            "health_status": "Healthy"
        })
        n_unhealthy = 600
        aug_unhealthy = pd.DataFrame({
            "temperature": np.random.choice([np.random.uniform(12.0, 16.5), np.random.uniform(26.5, 33.0)], n_unhealthy),
            "pH": np.random.choice([np.random.uniform(4.0, 5.5), np.random.uniform(6.8, 8.8)], n_unhealthy),
            "humidity": np.random.choice([np.random.uniform(30.0, 46.0), np.random.uniform(75.0, 92.0)], n_unhealthy),
            "water_level": np.random.choice([np.random.uniform(5.0, 35.0), np.random.uniform(45.0, 90.0)], n_unhealthy),
            "tds_ppm": np.random.choice([np.random.uniform(200.0, 500.0), np.random.uniform(980.0, 1400.0)], n_unhealthy),
            "health_status": "Unhealthy"
        })
        df = pd.concat([df, aug_healthy, aug_unhealthy], ignore_index=True)

    return df


def generate_remedy_steps(temperature: float, ph: float, humidity: float,
                          water_level: float, tds_ppm: float) -> Tuple[str, float, List[str], List[str]]:
    """
    Intelligent Agronomic Remedy Engine:
    Diagnoses anomalies in spinach telemetry and generates step-by-step measures
    to restore optimal plant health.
    """
    stress_factors = []
    remedy_steps = []
    penalties = 0.0

    # 1. pH Evaluation (Ideal: 5.8 - 6.5)
    if ph < 5.8:
        dev = 5.8 - ph
        penalties += min(35.0, dev * 25.0)
        stress_factors.append(f"Acidic Solution (pH {ph:.2f} < 5.80): Inhibits Calcium, Magnesium & Phosphorus absorption.")
        remedy_steps.append(
            f"Step 1 (pH Remedy): Dose 5–10 mL of dilute pH Up (potassium hydroxide/carbonate) per 10 L reservoir. "
            f"Allow water pump to circulate for 20 minutes and re-test until pH stabilizes between 5.8 and 6.5."
        )
    elif ph > 6.5:
        dev = ph - 6.5
        penalties += min(35.0, dev * 20.0)
        stress_factors.append(f"Alkaline Solution (pH {ph:.2f} > 6.50): Causes rapid Iron and Micronutrient lockout, triggering leaf yellowing/chlorosis.")
        remedy_steps.append(
            f"Step 1 (pH Remedy): Add 3–5 mL of food-grade pH Down (dilute phosphoric/nitric acid buffer). "
            f"Mix thoroughly. If leaf chlorosis has already appeared, administer foliar chelated iron (Fe-EDDHA 0.05%)."
        )

    # 2. Humidity Evaluation (Ideal: 50% - 70%)
    if humidity < 50.0:
        dev = 50.0 - humidity
        penalties += min(25.0, dev * 0.8)
        stress_factors.append(f"Low Humidity ({humidity:.1f}% < 50%): High vapor pressure deficit causes severe transpiration stress and leaf tip burn.")
        remedy_steps.append(
            f"Step 2 (Humidity Remedy): Engage ultrasonic humidifier or misting nozzles for 2 minutes every 15 minutes. "
            f"Adjust intake/exhaust air damper to bring grow room relative humidity to 55–65%."
        )
    elif humidity > 70.0:
        dev = humidity - 70.0
        penalties += min(25.0, dev * 0.8)
        stress_factors.append(f"Excessive Humidity ({humidity:.1f}% > 70%): Saturated leaf boundary layer creates prime conditions for fungal spores (Downy Mildew).")
        remedy_steps.append(
            f"Step 2 (Humidity Remedy): Turn on inline exhaust ventilation fans and internal oscillating canopy air fans "
            f"to improve air exchange and lower relative humidity below 65%."
        )

    # 3. Temperature Evaluation (Ideal: 18°C - 25°C)
    if temperature > 25.0:
        dev = temperature - 25.0
        penalties += min(25.0, dev * 3.0)
        stress_factors.append(f"Elevated Temperature ({temperature:.1f}°C > 25.0°C): Warm solution drops dissolved oxygen (DO) levels, risking Pythium root rot.")
        remedy_steps.append(
            f"Step 3 (Temperature Remedy): Activate inline nutrient reservoir chiller to maintain 18–22°C root zone temperature. "
            f"Increase air pump flow rate to oxygenate nutrient reservoir."
        )
    elif temperature < 18.0:
        dev = 18.0 - temperature
        penalties += min(25.0, dev * 2.5)
        stress_factors.append(f"Cold Temperature ({temperature:.1f}°C < 18.0°C): Stunts spinach metabolic uptake and slows vegetative leaf expansion.")
        remedy_steps.append(
            f"Step 3 (Temperature Remedy): Turn on submersible reservoir aquarium heater set to 20°C to maintain vigorous root metabolism."
        )

    # 4. Water Level Evaluation (Ideal: >= 40%)
    if water_level < 40.0:
        dev = 40.0 - water_level
        penalties += min(30.0, dev * 1.0)
        stress_factors.append(f"Low Reservoir Water Level ({water_level:.1f}% < 40%): Risk of pump dry-run and rapid nutrient salt concentration.")
        remedy_steps.append(
            f"Step 4 (Water Level Remedy): Top up nutrient tank immediately with fresh dechlorinated / reverse-osmosis water "
            f"until level reaches at least 80% capacity."
        )

    # 5. TDS / Nutrient PPM Evaluation (Ideal: 550 - 900 ppm)
    if tds_ppm < 550.0:
        dev = 550.0 - tds_ppm
        penalties += min(25.0, dev * 0.08)
        stress_factors.append(f"Nutrient Deficiency (TDS {tds_ppm:.1f} ppm < 550 ppm): Insufficient ionic nitrogen, potassium, and magnesium for vegetative spinach.")
        remedy_steps.append(
            f"Step 5 (Nutrient Remedy): Dose balanced Hydroponic Fertilizer Part A and Part B (1:1 ratio) until TDS reads 650–800 ppm."
        )
    elif tds_ppm > 900.0:
        dev = tds_ppm - 900.0
        penalties += min(25.0, dev * 0.06)
        stress_factors.append(f"High Nutrient Salinity (TDS {tds_ppm:.1f} ppm > 900 ppm): Risk of osmotic shock, root toxicity, and leaf margin scorch.")
        remedy_steps.append(
            f"Step 5 (Nutrient Remedy): Dilute the reservoir with 20% fresh pure RO water to bring TDS below 850 ppm."
        )

    health_score = max(5.0, min(100.0, 100.0 - penalties))

    if not stress_factors:
        status = "Healthy"
        remedy_steps.append("Plant is currently Healthy! All hydroponic parameters (pH, humidity, temperature, water level, TDS) are within optimal vegetative thresholds for Spinach. Maintain regular nutrient monitoring.")
    else:
        status = "Unhealthy"

    return status, round(health_score, 1), stress_factors, remedy_steps


def train_and_save():
    print("=" * 80)
    print("🥬 MODEL 1: TRAINING SPINACH PLANT HEALTH & REMEDY PREDICTION MODEL")
    print("=" * 80)

    df = load_spinach_dataset()

    feature_cols = ["temperature", "pH", "humidity", "water_level", "tds_ppm"]
    X = np.ascontiguousarray(df[feature_cols].to_numpy(dtype=np.float64))
    y = np.ascontiguousarray(df["health_status"].to_numpy(dtype=str))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=12,
        min_samples_split=4,
        random_state=42,
        class_weight="balanced"
    )

    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n[Model 1] Training Complete!")
    print(f"Validation Accuracy: {acc * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Feature Importance
    importances = clf.feature_importances_
    print("\nFeature Importances:")
    for col, imp in zip(feature_cols, importances):
        print(f"  - {col:15s}: {imp * 100:.2f}%")

    # Packaging Model Metadata
    model_artifact = {
        "model": clf,
        "feature_names": feature_cols,
        "classes": list(clf.classes_),
        "optimal_ranges": OPTIMAL_RANGES,
        "accuracy": acc
    }

    ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_artifact, MODEL_JOBLIB_PATH)
    joblib.dump(model_artifact, MODEL_PKL_PATH)

    print(f"\nSaved Model 1 to:")
    print(f"  - {MODEL_JOBLIB_PATH}")
    print(f"  - {MODEL_PKL_PATH}")


def predict_spinach_health(temperature: float, ph: float, humidity: float,
                           water_level: float, tds_ppm: float) -> Dict[str, Any]:
    """
    Inference function for Model 1:
    Predicts whether the spinach plant is Healthy or Unhealthy,
    and returns detailed corrective measures/remedies if unhealthy.
    """
    if not MODEL_JOBLIB_PATH.exists():
        raise FileNotFoundError(f"Model 1 artifact not found at {MODEL_JOBLIB_PATH}. Please run training first.")

    artifact = joblib.load(MODEL_JOBLIB_PATH)
    clf = artifact["model"]
    feature_names = artifact["feature_names"]

    x_input = np.array([[temperature, ph, humidity, water_level, tds_ppm]])
    pred_status = clf.predict(x_input)[0]
    probs = clf.predict_proba(x_input)[0]
    cls_idx = list(clf.classes_).index(pred_status)
    conf = float(probs[cls_idx]) * 100.0

    # Generate agronomic remedy recommendations
    rule_status, health_score, stress_factors, remedies = generate_remedy_steps(
        temperature=temperature,
        ph=ph,
        humidity=humidity,
        water_level=water_level,
        tds_ppm=tds_ppm
    )

    # Harmonize ML prediction with rule diagnostic
    final_status = "Unhealthy" if (pred_status == "Unhealthy" or rule_status == "Unhealthy") else "Healthy"

    return {
        "health_status": final_status,
        "confidence": f"{conf:.1f}%",
        "health_score": f"{health_score:.1f}%",
        "input_features": {
            "temperature": f"{temperature:.1f} °C",
            "pH": f"{ph:.2f}",
            "humidity": f"{humidity:.1f}%",
            "water_level": f"{water_level:.1f}%",
            "tds_ppm": f"{tds_ppm:.1f} ppm"
        },
        "stress_factors": stress_factors,
        "remedy_measures": remedies
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spinach Plant Health & Remedy Prediction Model")
    parser.add_argument("--train", action="store_true", help="Train and save the model")
    parser.add_argument("--temp", type=float, default=22.0, help="Temperature in °C")
    parser.add_argument("--ph", type=float, default=6.2, help="pH level")
    parser.add_argument("--humidity", type=float, default=60.0, help="Humidity in %")
    parser.add_argument("--water", type=float, default=85.0, help="Water level in %")
    parser.add_argument("--tds", type=float, default=700.0, help="TDS in ppm")

    args = parser.parse_args()

    if args.train:
        train_and_save()
    else:
        # Run inference test
        if not MODEL_JOBLIB_PATH.exists():
            print("[Model 1] Model artifact not found. Automatically training first...")
            train_and_save()

        result = predict_spinach_health(
            temperature=args.temp,
            ph=args.ph,
            humidity=args.humidity,
            water_level=args.water,
            tds_ppm=args.tds
        )

        print("\n" + "=" * 65)
        print("🌱 SPINACH PLANT HEALTH & REMEDY PREDICTION REPORT")
        print("=" * 65)
        print(f"Status      : {result['health_status']}")
        print(f"Confidence  : {result['confidence']}")
        print(f"Health Score: {result['health_score']}")
        print("-" * 65)
        print("Telemetry Features:")
        for k, v in result["input_features"].items():
            print(f"  * {k:14s}: {v}")
        print("-" * 65)
        if result["stress_factors"]:
            print("Detected Stress Factors:")
            for sf in result["stress_factors"]:
                print(f"  [!] {sf}")
            print("-" * 65)
        print("Recommended Remedy Measures:")
        for step in result["remedy_measures"]:
            print(f"  -> {step}")
        print("=" * 65)
