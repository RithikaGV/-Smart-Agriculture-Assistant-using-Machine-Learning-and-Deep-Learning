# Server data collector

Run from the repository root:

```powershell
py server_data/collect_server_data.py
```

The collector polls `http://192.168.100.131:5000/api/data` every 5 seconds and appends readings to `server_data/sensor_data.csv`. Use `Ctrl+C` to stop it. For a one-time connection check, run:

```powershell
py server_data/collect_server_data.py --once
```

The CSV includes a UTC `captured_at` timestamp and the spreadsheet columns `DHT_temp`, `pH`, `DHT_humidity`, `water_level`, and `Health_Status`. The server currently provides temperature, pH, and humidity; missing `water_level` and `Health_Status` values are left blank until those fields are available from its API.