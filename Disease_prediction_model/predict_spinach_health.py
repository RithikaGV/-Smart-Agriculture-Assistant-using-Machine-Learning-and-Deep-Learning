"""
Command-Line Runner for Model 1: Spinach Health & Remedy Suggester
Usage:
  python predict_spinach_health.py --ph 6.2 --humidity 60 --temp 22 --water 85 --tds 700
  python predict_spinach_health.py --ph 7.6 --humidity 42 --temp 29 --water 30 --tds 480
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model1_spinach_health_remedy import predict_spinach_health, train_and_save, MODEL_JOBLIB_PATH

def main():
    parser = argparse.ArgumentParser(description="Spinach Plant Health & Remedy Prediction")
    parser.add_argument("--ph", type=float, default=6.2, help="pH level of nutrient solution (e.g. 6.2)")
    parser.add_argument("--humidity", type=float, default=60.0, help="Relative humidity % (e.g. 60.0)")
    parser.add_argument("--temp", type=float, default=22.0, help="Water/Ambient temperature in °C (e.g. 22.0)")
    parser.add_argument("--water", type=float, default=85.0, help="Water reservoir level % (e.g. 85.0)")
    parser.add_argument("--tds", type=float, default=700.0, help="TDS nutrient level in ppm (e.g. 700.0)")

    args = parser.parse_args()

    if not MODEL_JOBLIB_PATH.exists():
        print("[Model 1] Model artifact not found. Training model now...")
        train_and_save()

    res = predict_spinach_health(
        temperature=args.temp,
        ph=args.ph,
        humidity=args.humidity,
        water_level=args.water,
        tds_ppm=args.tds
    )

    print("\n" + "=" * 70)
    print("🌱 SPINACH HEALTH & CORRECTIVE REMEDY PREDICTION REPORT")
    print("=" * 70)
    status_icon = "✅" if res["health_status"] == "Healthy" else "⚠️"
    print(f"Health Status : {status_icon} {res['health_status']}")
    print(f"Confidence    : {res['confidence']}")
    print(f"Health Score  : {res['health_score']}")
    print("-" * 70)
    print("Input Telemetry Readings:")
    for k, v in res["input_features"].items():
        print(f"  • {k:14s}: {v}")
    print("-" * 70)

    if res["stress_factors"]:
        print("Detected Stress Factor(s):")
        for factor in res["stress_factors"]:
            print(f"  🚨 {factor}")
        print("-" * 70)

    print("Recommended Action Steps & Remedies:")
    for i, remedy in enumerate(res["remedy_measures"], 1):
        print(f"  [{i}] {remedy}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
