"""
=============================================================================
Interactive Plant Leaf Disease Predictor (Model 2 CLI)
=============================================================================
Accepts an image of a plant leaf and predicts:
  1. Disease Name & Crop
  2. Prediction Confidence (%)
  3. Infection Severity (Healthy, Mild, Moderate, Severe)
  4. Biological Causal Pathogen & Symptoms
  5. Actionable Corrective Measures & Treatment Protocol

Usage:
  python predict_leaf.py [IMAGE_PATH]

Examples:
  python predict_leaf.py "C:\\Users\\NAVEENAMS\\Downloads\\ML_dataset_Disease_detection\\ML_dataset_Disease_detection\\Spinach\\Downy-Mildew(240)\\image (1).png"
  python predict_leaf.py "C:\\Users\\NAVEENAMS\\Downloads\\ML_dataset_Disease_detection\\ML_dataset_Disease_detection\\Spinach\\Healthy-Leaf(1399)\\image (1).png"
=============================================================================
"""

import sys
import os
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add ml_models to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model2_disease_prediction import predict_disease, MODEL_JOBLIB_PATH, train_and_save

def find_sample_leaf():
    """Auto-detects a sample leaf image to demonstrate inference if no arg given."""
    candidates = [
        Path(r"C:\Users\NAVEENAMS\Downloads\ML_dataset_Disease_detection\ML_dataset_Disease_detection\Spinach\Downy-Mildew(240)"),
        Path(r"C:\Users\NAVEENAMS\Downloads\ML_dataset_Disease_detection\ML_dataset_Disease_detection\Spinach\Anthracnose(102)"),
        Path(r"C:\Users\NAVEENAMS\Downloads\ML_dataset_Disease_detection\ML_dataset_Disease_detection\Spinach\Healthy-Leaf(1399)"),
        Path(__file__).resolve().parent / "sample_leaves"
    ]
    for c in candidates:
        if c.exists():
            for f in c.iterdir():
                if f.suffix.lower() in ('.jpg', '.jpeg', '.png'):
                    return str(f)
    return None

def main():
    if len(sys.argv) > 1:
        # Clean any accidental leading/trailing spaces or extra quotes
        image_path = " ".join(sys.argv[1:]).strip().strip('"').strip("'").strip()
    else:
        sample = find_sample_leaf()
        if sample:
            image_path = sample
            print(f"[Info] No image path passed. Testing with sample leaf from dataset:\n  -> {image_path}\n")
        else:
            print("[Error] Please specify an image path: python predict_leaf.py <path_to_leaf_image.jpg>")
            return

    if not os.path.exists(image_path):
        print(f"[Error] Image file not found: {image_path}")
        return

    if not MODEL_JOBLIB_PATH.exists():
        print("[Model 2] Model artifact not found. Automatically training first...")
        train_and_save()

    res = predict_disease(image_path)

    print("=" * 72)
    print("🌿 MODEL 2: PLANT LEAF DISEASE PREDICTION REPORT")
    print("=" * 72)
    print(f"Uploaded Image: {Path(image_path).name}")
    print("       ↓")
    print("AI Botanical Vision Classifier")
    print("       ↓")
    icon = "✅" if res["is_healthy"] else "🚨"
    print(f"Prediction    : {icon} {res['full_label']} — {res['confidence']}")
    print(f"Severity Level: {res['severity']}")
    print("-" * 72)
    print(f"Causal Agent  : {res['cause']}")
    print(f"Symptoms      : {res['symptoms']}")
    print("-" * 72)
    print("Corrective Measures & Actionable Treatment:")
    for i, step in enumerate(res["treatment_measures"], 1):
        print(f"  [{i}] {step}")
    print("-" * 72)
    print("Botanical Vision Indices:")
    for k, v in res["botanical_indices"].items():
        print(f"  • {k:22s}: {v}")
    print("=" * 72 + "\n")

if __name__ == "__main__":
    main()
