import json
import unittest
from unittest.mock import patch

import collect_server_data


class TestBackendReadingIngestion(unittest.TestCase):
    def test_sensor_mapping_and_request_payloads(self):
        row = {
            "captured_at": "2026-10-01T12:00:00+00:00",
            "DHT_temp": "23.5",
            "pH": "6.1",
            "DHT_humidity": "61",
            "water_level": "82",
        }
        backend_url = "http://localhost:8000/api/v1/sensors/ingest"

        with patch("collect_server_data.urlopen") as urlopen:
            payloads = collect_server_data.make_backend_payloads(row, "plant-123")
            for payload in payloads:
                collect_server_data.post_backend_reading(backend_url, payload)

        requests = [call.args[0] for call in urlopen.call_args_list]
        self.assertEqual(len(requests), 4)
        self.assertTrue(all(request.full_url == backend_url for request in requests))
        self.assertTrue(all(request.get_method() == "POST" for request in requests))
        self.assertEqual(
            [json.loads(request.data.decode("utf-8")) for request in requests],
            [
                {
                    "plant_id": "plant-123",
                    "sensor_type": "temperature",
                    "value": 23.5,
                    "unit": "°C",
                    "extra_data": {"captured_at": row["captured_at"]},
                },
                {
                    "plant_id": "plant-123",
                    "sensor_type": "ph",
                    "value": 6.1,
                    "unit": "pH",
                    "extra_data": {"captured_at": row["captured_at"]},
                },
                {
                    "plant_id": "plant-123",
                    "sensor_type": "humidity",
                    "value": 61.0,
                    "unit": "%",
                    "extra_data": {"captured_at": row["captured_at"]},
                },
                {
                    "plant_id": "plant-123",
                    "sensor_type": "waterLevel",
                    "value": 82.0,
                    "unit": "%",
                    "extra_data": {"captured_at": row["captured_at"]},
                },
            ],
        )

    def test_missing_and_non_numeric_readings_are_skipped(self):
        payloads = collect_server_data.make_backend_payloads(
            {
                "DHT_temp": "",
                "pH": "not-a-number",
                "DHT_humidity": None,
                "water_level": "inf",
            },
            "plant-123",
        )

        self.assertEqual(payloads, [])

    def test_server_url_payload_does_not_require_plant_id(self):
        payloads = collect_server_data.make_backend_payloads(
            {"DHT_temp": "23.5"},
            server_url="http://192.168.100.131:5000/api/data",
        )

        self.assertEqual(len(payloads), 1)
        self.assertNotIn("plant_id", payloads[0])
        self.assertEqual(payloads[0]["server_url"], "http://192.168.100.131:5000/api/data")
        self.assertEqual(payloads[0]["sensor_type"], "temperature")

    def test_health_label_uses_available_server_metrics(self):
        row = {
            "DHT_temp": "23.5",
            "pH": "6.1",
            "DHT_humidity": "61",
            "water_level": "",
        }

        cleaned = collect_server_data.make_cleaned_row(row)
        self.assertEqual(cleaned["Health_Status"], "healthy")
        self.assertEqual(cleaned["Reason"], "")

        row["pH"] = "8.09"
        cleaned = collect_server_data.make_cleaned_row(row)
        self.assertEqual(cleaned["Health_Status"], "Not healthy")
        self.assertIn("pH: Needs Immediate Attention", cleaned["Reason"])

    def test_no_available_metrics_waits_for_data(self):
        cleaned = collect_server_data.make_cleaned_row({
            "DHT_temp": "",
            "pH": None,
            "DHT_humidity": "",
            "water_level": None,
        })

        self.assertEqual(cleaned["Health_Status"], "Waiting for data")


if __name__ == "__main__":
    unittest.main()