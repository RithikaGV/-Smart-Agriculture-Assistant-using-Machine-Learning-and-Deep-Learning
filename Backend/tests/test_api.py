import unittest
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image
from app.db.session import SessionLocal
from app.models.domain import PlantServerConnection
from app.main import app

client = TestClient(app)

class TestHydroponicsAPI(unittest.TestCase):

    def setUp(self):
        login_payload = {
            "email": "rajesh.kumar@smartagri.org",
            "password": "password123"
        }
        res = client.post("/api/v1/auth/login", json=login_payload)
        token = res.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}

    def create_sensor_test_plant(self):
        response = client.post(
            "/api/v1/plants",
            json={"name": "Sensor Test Plant", "species": "Spinach"},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 201)
        plant_id = response.json()["id"]
        self.addCleanup(client.delete, f"/api/v1/plants/{plant_id}", headers=self.headers)
        return plant_id

    def ingest_metric(self, plant_id, sensor_type, value):
        response = client.post(
            "/api/v1/sensors/ingest",
            json={"plant_id": plant_id, "sensor_type": sensor_type, "value": value},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def get_active_plant_alerts(self, plant_id):
        response = client.get("/api/v1/alerts", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        return [alert for alert in response.json() if alert["plantId"] == plant_id and not alert["resolved"]]

    def test_01_root_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Machine Learning Hydroponic Assistant", response.json()["message"])

    def test_02_auth_flow(self):
        signup_payload = {
            "name": "Test Grower",
            "email": "testgrower@smartagri.org",
            "password": "testpassword123"
        }
        res = client.post("/api/v1/auth/signup", json=signup_payload)
        self.assertIn(res.status_code, [200, 400])
        
        login_payload = {
            "email": "testgrower@smartagri.org",
            "password": "testpassword123"
        }
        res = client.post("/api/v1/auth/login", json=login_payload)
        self.assertEqual(res.status_code, 200)
        token = res.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        res = client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_03_hierarchy_crud(self):
        expected_plant_id = self.create_sensor_test_plant()
        res = client.get("/api/v1/farms", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        farms = res.json()
        self.assertTrue(len(farms) > 0)
        systems = []
        for farm in farms:
            res = client.get(f"/api/v1/systems?farm_id={farm['id']}", headers=self.headers)
            self.assertEqual(res.status_code, 200)
            systems.extend(res.json())
        self.assertTrue(len(systems) > 0)
        plants = []
        for system in systems:
            res = client.get(f"/api/v1/plants?system_id={system['id']}", headers=self.headers)
            self.assertEqual(res.status_code, 200)
            plants.extend(res.json())
        self.assertIn(expected_plant_id, {plant["id"] for plant in plants})

    def test_04_plant_crud(self):
        payload = {
            "name": "Hydroponic Spinach Test",
            "species": "Spinach (Spinacia oleracea)",
            "location": "Bench 9",
            "notes": "Fast growth spinach variant"
        }
        res = client.post("/api/v1/plants", json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 201)
        created = res.json()
        plant_id = created["id"]
        self.assertEqual(created["name"], "Hydroponic Spinach Test")

        update_payload = {"notes": "Updated note for spinach"}
        res = client.put(f"/api/v1/plants/{plant_id}", json=update_payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res = client.delete(f"/api/v1/plants/{plant_id}", headers=self.headers)
        self.assertEqual(res.status_code, 204)

    def test_plant_server_ip_starts_unique_per_plant_collectors(self):
        created_plants = []
        collector_connections = []
        with (
            patch("app.api.v1.plants.plant_collector_manager.start") as start_collector,
            patch("app.api.v1.plants.plant_collector_manager.is_running", return_value=True),
        ):
            for _ in range(2):
                response = client.post(
                    "/api/v1/plants",
                    json={
                        "name": "Collector Tomato",
                        "species": "Tomato",
                        "server_ip": "192.168.100.131",
                    },
                    headers=self.headers,
                )
                self.assertEqual(response.status_code, 201)
                created_plants.append(response.json())
                collector_connections.append(start_collector.call_args.args[0])

        for plant in created_plants:
            self.addCleanup(client.delete, f"/api/v1/plants/{plant['id']}", headers=self.headers)
        for connection in collector_connections:
            self.addCleanup(Path(connection.raw_csv_path).unlink, missing_ok=True)
            self.addCleanup(Path(connection.cleaned_csv_path).unlink, missing_ok=True)

        self.assertEqual(start_collector.call_count, 2)
        self.assertTrue(all(plant["collectionStatus"] == "collecting" for plant in created_plants))
        self.assertTrue(all(plant["metrics"]["temperature"] is None for plant in created_plants))
        self.assertEqual(
            {connection.source_url for connection in collector_connections},
            {"http://192.168.100.131:5000/api/data"},
        )
        raw_paths = {Path(connection.raw_csv_path).name for connection in collector_connections}
        cleaned_paths = {Path(connection.cleaned_csv_path).name for connection in collector_connections}
        self.assertEqual(len(raw_paths), 2)
        self.assertEqual(len(cleaned_paths), 2)
        self.assertTrue(all(name.startswith("server_data_collector_tomato") for name in raw_paths))
        self.assertTrue(all(name.startswith("cleaned_server_data_collector_tomato") for name in cleaned_paths))
        self.assertTrue(all(Path(connection.raw_csv_path).is_file() for connection in collector_connections))
        self.assertTrue(all(Path(connection.cleaned_csv_path).is_file() for connection in collector_connections))

    def test_plant_rejects_invalid_server_address(self):
        response = client.post(
            "/api/v1/plants",
            json={"name": "Invalid Server Test", "species": "Tomato", "server_ip": "file:///data"},
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("HTTP or HTTPS", response.json()["detail"])

    def test_sensor_ingest_resolves_registered_server_without_plant_id(self):
        server_url = "http://192.168.100.140:5000/api/data"
        with patch("app.api.v1.plants.plant_collector_manager.start"):
            response = client.post(
                "/api/v1/plants",
                json={
                    "name": "URL Resolved Plant",
                    "species": "Tomato",
                    "server_ip": server_url,
                },
                headers=self.headers,
            )
        self.assertEqual(response.status_code, 201)
        plant_id = response.json()["id"]
        self.addCleanup(client.delete, f"/api/v1/plants/{plant_id}", headers=self.headers)
        db = SessionLocal()
        connection = db.query(PlantServerConnection).filter_by(plant_id=plant_id).first()
        db.close()
        self.assertIsNotNone(connection)
        self.addCleanup(Path(connection.raw_csv_path).unlink, missing_ok=True)
        self.addCleanup(Path(connection.cleaned_csv_path).unlink, missing_ok=True)

        reading = client.post(
            "/api/v1/sensors/ingest",
            json={"server_url": server_url, "sensor_type": "temperature", "value": 23.5, "unit": "°C"},
            headers=self.headers,
        )

        self.assertEqual(reading.status_code, 201)
        self.assertEqual(reading.json()["plant_id"], plant_id)
        self.assertEqual(reading.json()["metrics"]["temperature"], 23.5)

    def test_05_sensor_ingestion_and_alerts(self):
        target_plant_id = self.create_sensor_test_plant()

        ingest_payload = {
            "plant_id": target_plant_id,
            "sensor_type": "temperature",
            "value": 34.8,
            "unit": "°C"
        }
        res = client.post("/api/v1/sensors/ingest", json=ingest_payload, headers=self.headers)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["plant_status"], "Critical")

        res = client.get("/api/v1/alerts", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        alerts = res.json()
        critical_alerts = [a for a in alerts if a["plantId"] == target_plant_id and a["severity"] == "critical"]
        self.assertTrue(len(critical_alerts) > 0)
        alert_id = critical_alerts[0]["id"]

        res = client.post(f"/api/v1/alerts/{alert_id}/remedy", headers=self.headers)
        self.assertEqual(res.status_code, 200)

        res = client.get(f"/api/v1/plants/{target_plant_id}", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "Healthy")

    def test_sensor_ingestion_normal_metrics_create_no_alerts(self):
        plant_id = self.create_sensor_test_plant()
        initial = client.get(f"/api/v1/plants/{plant_id}", headers=self.headers).json()
        self.assertEqual(initial["status"], "Waiting for data")
        self.assertTrue(all(value is None for value in initial["metrics"].values()))

        expected_metrics = {
            "temperature": 23.0,
            "ph": 6.2,
            "humidity": 60.0,
            "waterLevel": 80.0,
        }

        first_reading = self.ingest_metric(plant_id, "temperature", 23.0)
        self.assertEqual(first_reading["plant_status"], "Healthy")

        for sensor_type, value in (
            ("ph", 6.2),
            ("humidity", 60.0),
            ("waterLevel", 80.0),
        ):
            result = self.ingest_metric(plant_id, sensor_type, value)

        self.assertEqual(result["plant_status"], "Healthy")
        self.assertEqual(result["metrics"], expected_metrics)
        self.assertEqual(self.get_active_plant_alerts(plant_id), [])

    def test_sensor_ingestion_unhealthy_metrics_create_unique_alerts_and_recover(self):
        plant_id = self.create_sensor_test_plant()
        unhealthy_readings = (
            ("temperature", 31.2),
            ("ph", 8.09),
            ("humidity", 74.0),
            ("waterLevel", 35.0),
        )

        for sensor_type, value in unhealthy_readings:
            result = self.ingest_metric(plant_id, sensor_type, value)

        alerts = self.get_active_plant_alerts(plant_id)
        self.assertEqual(result["plant_status"], "Critical")
        self.assertEqual({alert["type"] for alert in alerts}, {"Temperature", "pH", "Humidity", "Water Level"})
        self.assertEqual(
            {alert["type"]: alert["severity"] for alert in alerts},
            {"Temperature": "critical", "pH": "critical", "Humidity": "warning", "Water Level": "warning"},
        )

        for sensor_type, value in unhealthy_readings:
            self.ingest_metric(plant_id, sensor_type, value)
        self.assertEqual(len(self.get_active_plant_alerts(plant_id)), 4)

        temperature_alert = next(
            alert for alert in self.get_active_plant_alerts(plant_id) if alert["type"] == "Temperature"
        )
        remedy_response = client.post(
            f"/api/v1/alerts/{temperature_alert['id']}/remedy",
            headers=self.headers,
        )
        self.assertEqual(remedy_response.status_code, 200)
        remaining_alerts = self.get_active_plant_alerts(plant_id)
        self.assertEqual(len(remaining_alerts), 3)
        plant_response = client.get(f"/api/v1/plants/{plant_id}", headers=self.headers)
        self.assertEqual(plant_response.json()["status"], "Critical")

        for sensor_type, value in (
            ("temperature", 23.0),
            ("ph", 6.2),
            ("humidity", 60.0),
            ("waterLevel", 80.0),
        ):
            result = self.ingest_metric(plant_id, sensor_type, value)

        self.assertEqual(result["plant_status"], "Healthy")
        self.assertEqual(self.get_active_plant_alerts(plant_id), [])

    def test_06_dashboard_stats(self):
        res = client.get("/api/v1/dashboard/stats", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        stats = res.json()
        self.assertIn("totalPlants", stats)

    def test_07_ml_disease_prediction_upload(self):
        image_buffer = BytesIO()
        Image.new("RGB", (160, 160), color=(30, 150, 35)).save(image_buffer, format="PNG")
        res = client.post(
            "/api/v1/ml/predict-disease",
            files={"file": ("leaf.png", image_buffer.getvalue(), "image/png")},
        )
        self.assertEqual(res.status_code, 200)
        prediction = res.json()
        self.assertIn(prediction["plantType"], {"Spinach", "Cucumber", "Basil", "Tomato"})
        self.assertGreater(prediction["confidence"], 0)
        self.assertTrue(prediction["cause"])
        self.assertTrue(prediction["preventiveMeasures"])

    def test_08_ml_disease_prediction_from_url(self):
        image_buffer = BytesIO()
        Image.new("RGB", (160, 160), color=(30, 150, 35)).save(image_buffer, format="PNG")
        image_url = "https://8.8.8.8/leaf.png"
        with patch(
            "app.api.v1.ml.fetch_image_from_url",
            new_callable=AsyncMock,
            return_value=image_buffer.getvalue(),
        ) as fetch_image:
            res = client.post("/api/v1/ml/predict-disease-json", json={"image_url": image_url})

        self.assertEqual(res.status_code, 200)
        prediction = res.json()
        self.assertIn(prediction["plantType"], {"Spinach", "Cucumber", "Basil", "Tomato"})
        self.assertGreater(prediction["confidence"], 0)
        self.assertTrue(prediction["cause"])
        self.assertTrue(prediction["preventiveMeasures"])
        fetch_image.assert_awaited_once_with(image_url)

    def test_09_ml_disease_prediction_rejects_invalid_url(self):
        res = client.post("/api/v1/ml/predict-disease-json", json={"image_url": "file:///tmp/leaf.png"})

        self.assertEqual(res.status_code, 400)
        self.assertIn("HTTP or HTTPS", res.json()["detail"])

    def test_10_ml_disease_prediction_rejects_malformed_url(self):
        res = client.post("/api/v1/ml/predict-disease-json", json={"image_url": "http://[invalid"})

        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["detail"], "Image URL is malformed.")

    def test_11_ml_disease_prediction_reports_fetch_errors(self):
        with patch(
            "app.api.v1.ml.fetch_image_from_url",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=502, detail="Could not fetch the image URL."),
        ):
            res = client.post(
                "/api/v1/ml/predict-disease-json",
                json={"image_url": "https://8.8.8.8/leaf.png"},
            )

        self.assertEqual(res.status_code, 502)
        self.assertEqual(res.json()["detail"], "Could not fetch the image URL.")

    def test_12_ml_disease_prediction_rejects_invalid_fetched_image(self):
        with patch(
            "app.api.v1.ml.fetch_image_from_url",
            new_callable=AsyncMock,
            return_value=b"not an image",
        ):
            res = client.post(
                "/api/v1/ml/predict-disease-json",
                json={"image_url": "https://8.8.8.8/not-an-image"},
            )

        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid image", res.json()["detail"])

    def test_13_disease_model_artifact_loads(self):
        root_dir = Path(__file__).resolve().parents[2]
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))

        from Disease_prediction_model.model2_disease_prediction import MODEL_JOBLIB_PATH, predict_disease

        self.assertTrue(MODEL_JOBLIB_PATH.is_file())
        prediction = predict_disease(Image.new("RGB", (160, 160), color="green"))
        self.assertIn("full_label", prediction)

if __name__ == "__main__":
    unittest.main()
