import argparse
import csv
import json
import math
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


DEFAULT_URL = "http://192.168.100.131:5000/api/data"
DATA_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_OUTPUT = DATA_DIRECTORY / "server_data.csv"
LEGACY_OUTPUT = DATA_DIRECTORY / "sensor_data.csv"
DEFAULT_CLEANED_OUTPUT = DATA_DIRECTORY.parent / "Cleaned_server_data" / "cleaned_server_data.csv"
CSV_FIELDS = (
    "captured_at",
    "DHT_temp",
    "pH",
    "DHT_humidity",
    "water_level",
    "Health_Status",
)
CLEANED_FIELDS = (*CSV_FIELDS, "Reason")
HEALTH_RANGES = (
    ("Temperature", "DHT_temp", 18.0, 26.0, 15.0, 30.0),
    ("Humidity", "DHT_humidity", 50.0, 70.0, 40.0, 80.0),
    ("pH", "pH", 5.5, 6.5, 5.0, 7.0),
)
SOURCE_FIELDS = {
    "DHT_temp": ("DHT_temp", "dht_temp", "temp_avg", "temperature", "temperature1", "temp_hum_1_val1"),
    "pH": ("pH", "ph"),
    "DHT_humidity": ("DHT_humidity", "dht_humidity", "humidity_avg", "humidity", "humidity1"),
    "water_level": ("water_level", "waterLevel", "waterlevel"),
    "Health_Status": ("Health_Status", "health_status", "plant_status"),
}


def fetch_data(url):
    request = Request(url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("The server response must be a JSON object")

    data = payload.get("data", payload)
    if not isinstance(data, dict):
        raise ValueError("The server response's 'data' field must be a JSON object")
    return data


def make_row(data):
    row = {
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    for column, source_names in SOURCE_FIELDS.items():
        row[column] = next(
            (data[name] for name in source_names if name in data and data[name] is not None),
            "",
        )
    return row


def classify_metric(value, healthy_min, healthy_max, attention_min, attention_max):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "Reading unavailable"

    if not math.isfinite(number):
        return "Reading unavailable"
    if number < attention_min or number > attention_max:
        return "Needs Immediate Attention"
    if number < healthy_min or number > healthy_max:
        return "Alert"
    return "Healthy"


def make_cleaned_row(row):
    cleaned_row = {field: row.get(field, "") for field in CSV_FIELDS}
    reasons = []
    for label, field, healthy_min, healthy_max, attention_min, attention_max in HEALTH_RANGES:
        state = classify_metric(row.get(field), healthy_min, healthy_max, attention_min, attention_max)
        if state != "Healthy":
            reasons.append(f"{label}: {state}")

    cleaned_row["Health_Status"] = "healthy" if not reasons else "Not healthy"
    cleaned_row["Reason"] = "; ".join(reasons)
    return cleaned_row


def rebuild_cleaned_data(source_path, cleaned_path):
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    with cleaned_path.open("w", newline="", encoding="utf-8") as cleaned_file:
        writer = csv.DictWriter(cleaned_file, fieldnames=CLEANED_FIELDS)
        writer.writeheader()
        if source_path.exists():
            with source_path.open("r", newline="", encoding="utf-8") as source_file:
                for row in csv.DictReader(source_file):
                    writer.writerow(make_cleaned_row(row))


def append_row(output_path, row, fieldnames=CSV_FIELDS):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not output_path.exists() or output_path.stat().st_size == 0
    with output_path.open("a", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        if needs_header:
            writer.writeheader()
        writer.writerow(row)
        output_file.flush()


def main():
    parser = argparse.ArgumentParser(description="Continuously collect sensor readings from the greenhouse server.")
    parser.add_argument("--url", default=DEFAULT_URL, help="JSON endpoint to poll")
    parser.add_argument("--interval", type=float, default=5, help="Seconds between polls (default: 5)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="CSV file to append readings to")
    parser.add_argument("--cleaned-output", type=Path, default=DEFAULT_CLEANED_OUTPUT, help="CSV file for classified readings")
    parser.add_argument("--once", action="store_true", help="Collect one reading and exit")
    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("--interval must be greater than zero")
    if args.output.resolve() == args.cleaned_output.resolve():
        parser.error("--output and --cleaned-output must be different files")

    if args.output == DEFAULT_OUTPUT and not args.output.exists() and LEGACY_OUTPUT.exists():
        shutil.copyfile(LEGACY_OUTPUT, args.output)
    rebuild_cleaned_data(args.output, args.cleaned_output)

    print(f"Polling {args.url}; raw data: {args.output}; cleaned data: {args.cleaned_output}", flush=True)
    try:
        while True:
            try:
                row = make_row(fetch_data(args.url))
                append_row(args.output, row)
                append_row(args.cleaned_output, make_cleaned_row(row), CLEANED_FIELDS)
                print(f"Captured {row['captured_at']}", flush=True)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                print(f"Collection failed: {error}", file=sys.stderr, flush=True)

            if args.once:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Collection stopped.", flush=True)


if __name__ == "__main__":
    main()