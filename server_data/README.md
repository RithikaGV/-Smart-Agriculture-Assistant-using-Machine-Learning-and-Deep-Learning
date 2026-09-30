# Server data collector

Run from the repository root:

```powershell
py server_data/collect_server_data.py
```

The collector polls `http://192.168.100.131:5000/api/data` every 5 seconds and appends raw readings to `server_data/server_data.csv`. It also rebuilds and continuously updates `Cleaned_server_data/cleaned_server_data.csv` from all existing and newly collected rows. Use `Ctrl+C` to stop it. For a one-time connection check, run:

```powershell
py server_data/collect_server_data.py --once
```

The raw CSV includes a UTC `captured_at` timestamp and the spreadsheet columns `DHT_temp`, `pH`, `DHT_humidity`, `water_level`, and `Health_Status`. On first run, existing rows in `sensor_data.csv` are copied into `server_data.csv` and retained. The cleaned CSV adds a `Reason` column and derives `Health_Status` from temperature, humidity, and pH using the healthy ranges in the supplied table. Healthy endpoints are inclusive; out-of-range values are marked `Alert` or `Needs Immediate Attention`. Missing readings are marked `Not healthy` with the unavailable metric listed in `Reason`.