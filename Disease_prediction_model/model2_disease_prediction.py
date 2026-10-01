"""
=============================================================================
MODEL 2: Image-Based Plant Disease Detection & Remedy Prediction Model
=============================================================================
Dataset: Plant Disease Image Dataset (C:\\Users\\NAVEENAMS\\Downloads\\ML_dataset_Disease_detection)
Architecture:
  Plant / Leaf Image
         ↓
  Leaf Foreground Mask & Preprocessing (160x160)
         ↓
  Agronomic Botanical Feature Extraction (27 Botanical Indices & Distributions)
         ↓
  StandardScaler + ExtraTrees / RandomForest Classifier
         ↓
  Disease Name + Confidence Score (%) + Severity + Corrective Measures
=============================================================================
"""

import io
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Union, Tuple, List
import numpy as np
from PIL import Image
import joblib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

BASE_DIR = Path(__file__).resolve().parent.parent
ML_MODELS_DIR = Path(__file__).resolve().parent

MODEL_JOBLIB_PATH = ML_MODELS_DIR / "model2_disease_prediction.joblib"
MODEL_PKL_PATH = ML_MODELS_DIR / "model2_disease_prediction.pkl"

DATASET_ROOT = Path(r"C:\Users\NAVEENAMS\Downloads\ML_dataset_Disease_detection\ML_dataset_Disease_detection")

# Class Definitions mapped to dataset subdirectories
DATASET_CLASS_MAP = {
    "Spinach___Anthracnose": {
        "crop": "Spinach",
        "disease": "Anthracnose",
        "subpath": "Spinach/Anthracnose(102)",
        "cause": "Fungal pathogen (*Colletotrichum dematium*) promoted by free moisture on leaf foliage.",
        "symptoms": "Water-soaked circular lesions that turn tan-brown with dark sunken concentric rings.",
        "treatment": [
            "Prune and discard infected leaves immediately to halt airborne fungal spore spread.",
            "Apply bio-fungicide containing Bacillus subtilis or organic copper octanoate spray.",
            "Reduce ambient humidity below 65% and eliminate any overhead water splashes on foliage."
        ]
    },
    "Spinach___Bacterial_Spot": {
        "crop": "Spinach",
        "disease": "Bacterial Spot",
        "subpath": "Spinach/Bacterial-Spot(752)",
        "cause": "Bacterial pathogen (*Pseudomonas syringae pv. spinaciae*) entering leaf stomata.",
        "symptoms": "Dark angular water-soaked spots with distinct chlorotic yellow halos across leaf blade.",
        "treatment": [
            "Sterilize shears in 70% isopropyl alcohol and excise symptomatic foliage.",
            "Spray fixed copper hydroxide or biological Streptomyces lydicus bactericide.",
            "Sanitize reservoir water with 3% food-grade H2O2 (1-2 mL/L) to prevent system-wide recirculation.",
            "Maintain continuous canopy ventilation to accelerate leaf boundary layer drying."
        ]
    },
    "Spinach___Downy_Mildew": {
        "crop": "Spinach",
        "disease": "Downy Mildew",
        "subpath": "Spinach/Downy-Mildew(240)",
        "cause": "Oomycete pathogen (*Peronospora effusa*) flourishing in high humidity (>75%) and cool temperatures.",
        "symptoms": "Irregular chlorotic yellow patches on upper leaf surface with purplish-gray mildew on underside.",
        "treatment": [
            "Immediately lower grow room relative humidity to 50–60% using dehumidifiers and exhaust fans.",
            "Apply potassium phosphite (mono- and dipotassium salts of phosphorous acid) or bio-fungicide.",
            "Widen plant spacing in hydroponic raft/channels to maximize horizontal airflow.",
            "Avoid reservoir water temperatures dropping below 17°C during vegetative growth."
        ]
    },
    "Spinach___Healthy_Leaf": {
        "crop": "Spinach",
        "disease": "Healthy Leaf",
        "subpath": "Spinach/Healthy-Leaf(1399)",
        "cause": "Optimal hydroponic nutrient balance and environmental regulation.",
        "symptoms": "Vibrant emerald green foliage, uniform chlorophyll distribution, robust cellular turgor, zero lesions.",
        "treatment": [
            "Plant is Healthy! Maintain optimal spinach hydroponic parameters:",
            "  • pH: 5.8 – 6.5",
            "  • Relative Humidity: 50% – 68%",
            "  • Temperature: 18°C – 24°C",
            "  • TDS / EC: 600 – 850 ppm (1.2 – 1.7 mS/cm)",
            "Continue standard 14–16 hour photoperiod cycle."
        ]
    },
    "Spinach___Pest_Damage": {
        "crop": "Spinach",
        "disease": "Pest Damage",
        "subpath": "Spinach/Pest-Damage(513)",
        "cause": "Infestation by thrips, aphids, leaf miners, or caterpillars chewing and stippling foliage.",
        "symptoms": "Perforated leaf margins, irregular chew holes, silvery stippling with tiny dark fecal specks.",
        "treatment": [
            "Deploy yellow and blue sticky insect monitoring cards around hydroponic grow beds.",
            "Apply cold-pressed organic neem oil spray (0.5% emulsion with mild soap) during dark lights-off cycle.",
            "Introduce beneficial biological control insects such as green lacewing larvae or predatory mites.",
            "Inspect underside of leaves daily and gently hand-remove visible caterpillars or egg clusters."
        ]
    },
    "Cucumber___Powdery_Mildew": {
        "crop": "Cucumber",
        "disease": "Powdery Mildew",
        "subpath": "Cucumber/Powdery_mildew",
        "cause": "Obligate biotrophic fungal pathogen (*Podosphaera xanthii*).",
        "symptoms": "Talcum powder-like white circular fungal colonies spreading across leaf surface.",
        "treatment": [
            "Spray dilute potassium bicarbonate solution (3 g/L) or emulsified horticultural oil.",
            "Increase canopy air circulation and lower atmospheric humidity to prevent spore attachment.",
            "Prune older heavily covered lower leaves to improve light penetration."
        ]
    },
    "Cucumber___Downy_Mildew": {
        "crop": "Cucumber",
        "disease": "Downy Mildew",
        "subpath": "Cucumber/Downy_mildew",
        "cause": "Oomycete pathogen (*Pseudoperonospora cubensis*).",
        "symptoms": "Angular yellow chlorotic lesions bounded strictly by leaf veins on upper leaf surface.",
        "treatment": [
            "Apply systemic phosphonate fungicide or copper soap protectant.",
            "Maintain dry foliage and ensure grow lights provide adequate warmth to keep leaf canopy dry."
        ]
    },
    "Cucumber___Healthy": {
        "crop": "Cucumber",
        "disease": "Healthy Leaf",
        "subpath": "Cucumber/Healthy_leaves",
        "cause": "Optimal hydroponic nutrient concentration and balanced lighting.",
        "symptoms": "Robust deep green cucumber leaves with uniform venation and zero chlorosis or powdery spots.",
        "treatment": [
            "Plant is Healthy! Maintain cucumber hydroponic EC 1.8–2.4 mS/cm, pH 5.8–6.2, and humidity 60–70%."
        ]
    },
    "Basil___Fusarium_Wilt": {
        "crop": "Basil",
        "disease": "Fusarium Wilt",
        "subpath": "Basil/Fusarium_Wilt",
        "cause": "Soilborne/waterborne vascular fungal pathogen (*Fusarium oxysporum f. sp. basilicum*).",
        "symptoms": "Unilateral leaf curling, brown vascular discoloration of stem, sudden irreversible wilting.",
        "treatment": [
            "Immediately rogue and discard infected plants; do not compost in hydroponic facilities.",
            "Thoroughly drain and sterilize the hydroponic reservoir and feed lines with dilute H2O2."
        ]
    },
    "Basil___Sun_Scald_Burn": {
        "crop": "Basil",
        "disease": "Sun Scald / Light Burn",
        "subpath": "Basil/Sun_Scald_Burn",
        "cause": "Excessive light intensity (PPFD > 450 µmol/m²/s) or thermal heat radiation scorching tender foliage.",
        "symptoms": "Bleached, dry papery white or straw-colored scorched patches between leaf veins with brittle margins.",
        "treatment": [
            "Raise LED grow fixtures 15–20 cm higher above the canopy or dim lighting intensity by 25%.",
            "Verify grow room temperature does not exceed 26°C and improve canopy air circulation with oscillating fans.",
            "Prune irreparably scorched leaves to encourage fresh auxiliary vegetative shoot growth."
        ]
    },
    "Basil___Healthy": {
        "crop": "Basil",
        "disease": "Healthy Leaf",
        "subpath": "Basil/Healthy",
        "cause": "Optimal photosynthetic lighting and nutrient balance.",
        "symptoms": "Lush vibrant green aromatic foliage with uniform chlorophyll and zero scorch or wilting.",
        "treatment": [
            "Maintain current lighting (PPFD ~300 µmol/m²/s), pH 5.8–6.4, and TDS 700–900 ppm."
        ]
    },
    "Tomato___Early_Blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "subpath": "Tomato/Tomato___Early_blight",
        "cause": "Fungal pathogen (*Alternaria solani*).",
        "symptoms": "Dark brown concentric rings forming distinctive 'bullseye' target lesions on foliage.",
        "treatment": [
            "Remove lower infected foliage touching hydroponic channels.",
            "Spray copper octanoate or Bacillus amyloliquefaciens bio-fungicide weekly."
        ]
    }
}


def preprocess_and_extract_features(image_input: Union[str, Path, bytes, Image.Image]) -> np.ndarray:
    """
    Agronomic Botanical Feature Extraction:
    Standardizes image to 160x160, masks foreground leaf tissue, and
    computes 39 botanical computer vision metrics (moments, agronomic indices,
    lesion signatures, texture gradients, and chromatic histograms).
    """
    if isinstance(image_input, (str, Path)):
        img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, (bytes, bytearray)):
        img = Image.open(io.BytesIO(image_input)).convert("RGB")
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    img = img.resize((160, 160))
    arr = np.array(img, dtype=np.float32) / 255.0

    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # Convert to HSV color space
    hsv = img.convert("HSV")
    hsv_arr = np.array(hsv, dtype=np.float32)
    h, s, v = hsv_arr[:, :, 0] / 255.0, hsv_arr[:, :, 1] / 255.0, hsv_arr[:, :, 2] / 255.0

    # Robust foreground leaf mask (isolates plant foliage from background)
    leaf_mask = (g > 0.16) | (r + g > 0.32) | ((r > 0.12) & (r > g * 1.05))
    if np.sum(leaf_mask) < 150:
        leaf_mask = np.ones_like(r, dtype=bool)

    r_f, g_f, b_f = r[leaf_mask], g[leaf_mask], b[leaf_mask]
    h_f, s_f, v_f = h[leaf_mask], s[leaf_mask], v[leaf_mask]

    # 1. Color channel moments (Mean & Std Dev)
    m_r, m_g, m_b = float(np.mean(r_f)), float(np.mean(g_f)), float(np.mean(b_f))
    s_r, s_g, s_b = float(np.std(r_f)), float(np.std(g_f)), float(np.std(b_f))
    m_h, m_s, m_v = float(np.mean(h_f)), float(np.mean(s_f)), float(np.mean(v_f))
    s_h, s_s, s_v = float(np.std(h_f)), float(np.std(s_f)), float(np.std(v_f))

    # 2. Agronomic botanical color indices
    exg = float(np.mean(2.0 * g_f - r_f - b_f))                                      # Excess Green Index
    exr = float(np.mean(1.4 * r_f - g_f))                                            # Excess Red Index
    exgr = exg - exr                                                                 # Difference Index
    vari = float(np.mean((g_f - r_f) / (g_f + r_f - b_f + 1e-5)))                   # Visible Atmospherically Resistant
    ndyi = float(np.mean((g_f - b_f) / (g_f + b_f + 1e-5)))                         # Normalized Yellowness Index
    rg_ratio = float(np.mean(r_f / (g_f + 1e-5)))                                    # Red/Green ratio
    bg_ratio = float(np.mean(b_f / (g_f + 1e-5)))

    # 3. Disease lesion signatures
    powdery = float(np.mean((v_f > 0.65) & (s_f < 0.40)))                           # White fungal powder
    necrotic_dark = float(np.mean((r_f > g_f) & (v_f < 0.35)))                       # Dark necrotic spots
    necrotic_tan = float(np.mean((r_f > 0.4) & (g_f > 0.25) & (b_f < 0.25) & (r_f > g_f * 1.2))) # Tan anthracnose
    chlorotic_yellow = float(np.mean((r_f > 0.40) & (g_f > 0.40) & (b_f < 0.28)))    # Yellow halos / downy mildew

    # 4. Spatial gradients and texture roughness
    diff_r_x, diff_r_y = np.diff(r, axis=1), np.diff(r, axis=0)
    diff_g_x, diff_g_y = np.diff(g, axis=1), np.diff(g, axis=0)
    grad_r = float(np.var(diff_r_x) + np.var(diff_r_y))
    grad_g = float(np.var(diff_g_x) + np.var(diff_g_y))
    grad_mag = float(np.mean(np.sqrt(diff_g_x[:-1, :]**2 + diff_g_y[:, :-1]**2)))

    # 5. Hue & Saturation histograms
    h_hist, _ = np.histogram(h_f, bins=8, range=(0, 1), density=True)
    s_hist, _ = np.histogram(s_f, bins=4, range=(0, 1), density=True)

    # 6. Shannon Entropy of Hue
    p = h_hist[h_hist > 0]
    p_norm = p / np.sum(p)
    entropy = -float(np.sum(p_norm * np.log2(p_norm + 1e-9)))

    features = [
        m_r, m_g, m_b, s_r, s_g, s_b,
        m_h, m_s, m_v, s_h, s_s, s_v,
        exg, exr, exgr, vari, ndyi, rg_ratio, bg_ratio,
        powdery, necrotic_dark, necrotic_tan, chlorotic_yellow,
        grad_r, grad_g, grad_mag, entropy
    ] + list(h_hist) + list(s_hist)

    return np.array(features, dtype=np.float32)


def train_and_save():
    print("=" * 80)
    print("🍃 MODEL 2: TRAINING IMAGE-BASED PLANT DISEASE DETECTION MODEL")
    print("=" * 80)

    if not DATASET_ROOT.exists():
        raise FileNotFoundError(f"Plant disease dataset directory not found at: {DATASET_ROOT}")

    X, y = [], []
    samples_per_class = 120

    print(f"[Model 2] Sampling up to {samples_per_class} images per disease class from:\n  {DATASET_ROOT}\n")

    for cls_key, meta in DATASET_CLASS_MAP.items():
        cls_dir = DATASET_ROOT / Path(meta["subpath"])
        if not cls_dir.exists():
            print(f"  [!] Warning: Folder not found: {cls_dir}. Skipping.")
            continue

        imgs = [f for f in cls_dir.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')][:samples_per_class]
        print(f"  * {cls_key:28s}: {len(imgs)} images loaded from {meta['subpath']}")

        for img_p in imgs:
            try:
                feat = preprocess_and_extract_features(img_p)
                X.append(feat)
                y.append(cls_key)
            except Exception as e:
                continue

    X = np.ascontiguousarray(X, dtype=np.float64)
    y = np.ascontiguousarray(y, dtype=str)

    print(f"\n[Model 2] Extracted features for {len(X)} images across {len(np.unique(y))} disease classes.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", ExtraTreesClassifier(
            n_estimators=180,
            max_depth=18,
            min_samples_split=3,
            random_state=42,
            class_weight="balanced"
        ))
    ])

    print("[Model 2] Fitting ExtraTrees botanical classifier...")
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\n[Model 2] Training Complete! Validation Accuracy: {acc * 100:.2f}%\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    model_artifact = {
        "pipeline": pipe,
        "classes": list(pipe.classes_),
        "class_meta": DATASET_CLASS_MAP,
        "accuracy": acc
    }

    ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_artifact, MODEL_JOBLIB_PATH)
    joblib.dump(model_artifact, MODEL_PKL_PATH)

    print(f"\nSaved Model 2 to:")
    print(f"  - {MODEL_JOBLIB_PATH}")
    print(f"  - {MODEL_PKL_PATH}")


def predict_disease(image_input: Union[str, Path, bytes, Image.Image]) -> Dict[str, Any]:
    """
    Inference function for Model 2:
    Accepts plant leaf image and predicts:
      - disease name (e.g. "Downy Mildew")
      - crop (e.g. "Spinach")
      - full label (e.g. "Spinach - Downy Mildew")
      - confidence score (%)
      - severity level ("Healthy", "Mild", "Moderate", "Severe")
      - symptoms & causal agent
      - step-by-step corrective treatment measures
    """
    if not MODEL_JOBLIB_PATH.exists():
        raise FileNotFoundError(f"Model 2 artifact not found at {MODEL_JOBLIB_PATH}. Please train the model first.")

    artifact = joblib.load(MODEL_JOBLIB_PATH)
    pipe = artifact["pipeline"]
    classes = artifact["classes"]
    meta_db = artifact["class_meta"]

    # Extract features
    features = preprocess_and_extract_features(image_input)
    x_input = np.ascontiguousarray([features], dtype=np.float64)

    # Predict class & confidence
    pred_cls = pipe.predict(x_input)[0]
    probs = pipe.predict_proba(x_input)[0]
    cls_idx = list(classes).index(pred_cls)
    conf = float(probs[cls_idx]) * 100.0

    meta = meta_db.get(pred_cls, {
        "crop": "Plant",
        "disease": pred_cls,
        "cause": "Unknown pathogen or environmental stress.",
        "symptoms": "Leaf discoloration and lesion symptoms detected.",
        "treatment": ["Inspect foliage and consult local agricultural extension."]
    })

    # Estimate severity based on lesion indices
    # powdery (feat[19]), necrotic_dark (feat[20]), necrotic_tan (feat[21]), chlorotic_yellow (feat[22])
    lesion_ratio = float(features[19] + features[20] + features[21] + features[22])
    if "Healthy" in pred_cls:
        severity = "Healthy"
    elif lesion_ratio < 0.10:
        severity = "Mild (Early Stage)"
    elif lesion_ratio < 0.25:
        severity = "Moderate"
    else:
        severity = "Severe"

    return {
        "full_label": f"{meta['crop']} - {meta['disease']}",
        "crop": meta["crop"],
        "disease": meta["disease"],
        "disease_name": meta["disease"],
        "confidence": f"{conf:.1f}%",
        "confidence_pct": round(conf, 1),
        "formatted_output": f"{meta['crop']} - {meta['disease']} — {conf:.0f}%",
        "severity": severity,
        "is_healthy": "Healthy" in pred_cls,
        "status": "Healthy" if "Healthy" in pred_cls else "Diseased",
        "cause": meta["cause"],
        "symptoms": meta["symptoms"],
        "treatment_recommendation": " ".join(meta["treatment"]),
        "treatment_measures": meta["treatment"],
        "probabilities": {cls_name: round(float(p) * 100.0, 1) for cls_name, p in zip(classes, probs)},
        "botanical_indices": {
            "excess_green_index": round(float(features[12]), 3),
            "chlorosis_index_ndyi": round(float(features[16]), 3),
            "lesion_density": f"{lesion_ratio * 100:.1f}%",
            "texture_gradient": round(float(features[25]), 3)
        }
    }

# Alias for backwards compatibility
predict_leaf_disease = predict_disease


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plant Disease Detection Model 2")
    parser.add_argument("--train", action="store_true", help="Train and save Model 2")
    parser.add_argument("--image", type=str, help="Path to leaf image for disease prediction")

    args = parser.parse_args()

    if args.train:
        train_and_save()
    elif args.image:
        result = predict_disease(args.image)
        print("\n" + "=" * 70)
        print("🍃 PLANT DISEASE PREDICTION REPORT (MODEL 2)")
        print("=" * 70)
        print(f"Prediction    : {result['full_label']}")
        print(f"Confidence    : {result['confidence']}")
        print(f"Severity      : {result['severity']}")
        print(f"Causal Agent  : {result['cause']}")
        print("-" * 70)
        print(f"Symptoms      : {result['symptoms']}")
        print("-" * 70)
        print("Corrective Measures & Treatment:")
        for step in result["treatment_measures"]:
            print(f"  -> {step}")
        print("-" * 70)
        print("Botanical Features:")
        for k, v in result["botanical_indices"].items():
            print(f"  • {k:22s}: {v}")
        print("=" * 70 + "\n")
    else:
        print("Please provide --train to train Model 2 or --image <path> to test prediction.")
