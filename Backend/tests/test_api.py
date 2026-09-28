import unittest
from fastapi.testclient import TestClient
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
        res = client.get("/api/v1/farms", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        farms = res.json()
        self.assertTrue(len(farms) > 0)
        farm_id = farms[0]["id"]

        res = client.get(f"/api/v1/systems?farm_id={farm_id}", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        systems = res.json()
        self.assertTrue(len(systems) > 0)
        sys_id = systems[0]["id"]

        res = client.get(f"/api/v1/plants?system_id={sys_id}", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        plants = res.json()
        self.assertTrue(len(plants) > 0)

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

    def test_05_sensor_ingestion_and_alerts(self):
        res = client.get("/api/v1/plants", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        plants = res.json()
        self.assertTrue(len(plants) > 0)
        target_plant_id = plants[0]["id"]

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

    def test_06_dashboard_stats(self):
        res = client.get("/api/v1/dashboard/stats", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        stats = res.json()
        self.assertIn("totalPlants", stats)

    def test_07_ml_disease_prediction(self):
        res = client.post("/api/v1/ml/predict-disease-json", json={"image_url": "https://example.com/leaf.jpg"})
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
