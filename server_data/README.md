# Server data collector

Run from the repository root:

```powershell
py server_data/collect_server_data.py
```

The collector polls `http://192.168.100.131:5000/api/data` every 5 seconds and appends raw readings to `server_data/server_data.csv`. It also rebuilds and continuously updates `Cleaned_server_data/cleaned_server_data.csv` from all existing and newly collected rows. Use `Ctrl+C` to stop it. For a one-time connection check, run:

```powershell
py server_data/collect_server_data.py --once
```

To manually send readings to a plant already connected in the app, provide the full ingest URL. The backend resolves the plant from its registered server URL, so no plant ID is needed. CSV collection continues if a backend request fails:

```powershell
py server_data/collect_server_data.py `
	--url http://192.168.100.131:5000/api/data `
	--backend-url http://localhost:8000/api/v1/sensors/ingest
```

Backend ingestion is disabled unless `--backend-url` is provided. The source URL must match a server URL already registered to a plant in the app. Temperature, pH, humidity, and water-level readings are sent separately; missing and non-numeric values are skipped. The app normally starts this collector automatically when a plant is added.

The raw CSV includes a UTC `captured_at` timestamp and the columns `DHT_temp`, `pH`, `DHT_humidity`, `water_level`, and `Health_Status`. On first run, existing rows in `sensor_data.csv` are copied into `server_data.csv` and retained. The cleaned CSV adds a `Reason` column and derives `Health_Status` from available temperature, humidity, pH, and water-level readings. Missing fields are ignored so servers that report only three metrics can still produce a health label; if no metrics are available, the label is `Waiting for data`. Healthy endpoints are inclusive; out-of-range values are marked `Alert` or `Needs Immediate Attention`.