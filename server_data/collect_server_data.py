import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


DEFAULT_URL = "http://192.168.100.131:5000/api/data"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "sensor_data.csv"
CSV_FIELDS = (
    "captured_at",
    "DHT_temp",
    "pH",
    "DHT_humidity",
    "water_level",
    "Health_Status",
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


def append_row(output_path, row):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    needs_header = not output_path.exists() or output_path.stat().st_size == 0
    with output_path.open("a", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=CSV_FIELDS)
        if needs_header:
            writer.writeheader()
        writer.writerow(row)
        output_file.flush()


def main():
    parser = argparse.ArgumentParser(description="Continuously collect sensor readings from the greenhouse server.")
    parser.add_argument("--url", default=DEFAULT_URL, help="JSON endpoint to poll")
    parser.add_argument("--interval", type=float, default=5, help="Seconds between polls (default: 5)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="CSV file to append readings to")
    parser.add_argument("--once", action="store_true", help="Collect one reading and exit")
    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("--interval must be greater than zero")

    print(f"Polling {args.url}; appending to {args.output}", flush=True)
    try:
        while True:
            try:
                row = make_row(fetch_data(args.url))
                append_row(args.output, row)
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