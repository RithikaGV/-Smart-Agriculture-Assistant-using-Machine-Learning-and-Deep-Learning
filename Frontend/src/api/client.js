const API_BASE_URL = "http://localhost:8000/api/v1";

export const getAuthToken = () => {
  return localStorage.getItem("hydro_access_token") || "";
};

export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem("hydro_access_token", token);
  } else {
    localStorage.removeItem("hydro_access_token");
  }
};

const request = async (endpoint, options = {}) => {
  const token = getAuthToken();
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
  const headers = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP Error ${res.status}`);
    }

    if (res.status === 204) return null;
    return await res.json();
  } catch (err) {
    console.warn(`[API Client Warning] ${endpoint}: ${err.message}.`);
    throw err;
  }
};

export const api = {
  // Auth
  login: (email, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  signup: (growerData) =>
    request("/auth/signup", {
      method: "POST",
      body: JSON.stringify(growerData),
    }),

  getProfile: () => request("/auth/me"),

  updateProfile: (profileData) =>
    request("/auth/me", {
      method: "PUT",
      body: JSON.stringify(profileData),
    }),

  // Hierarchy: Farms & Systems
  getFarms: () => request("/farms"),
  getSystems: (farmId) => request(`/systems${farmId ? `?farm_id=${farmId}` : ""}`),

  // Plants CRUD
  getPlants: () => request("/plants"),
  createPlant: (plantData) =>
    request("/plants", {
      method: "POST",
      body: JSON.stringify(plantData),
    }),
  updatePlant: (plantId, plantData) =>
    request(`/plants/${plantId}`, {
      method: "PUT",
      body: JSON.stringify(plantData),
    }),
  deletePlant: (plantId) =>
    request(`/plants/${plantId}`, {
      method: "DELETE",
    }),

  // Sensors
  connectSensor: (plantId, sensorType, address) =>
    request("/sensors/connect", {
      method: "POST",
      body: JSON.stringify({ plant_id: plantId, sensor_type: sensorType, address }),
    }),
  ingestReading: (plantId, sensorType, value, unit = "") =>
    request("/sensors/ingest", {
      method: "POST",
      body: JSON.stringify({ plant_id: plantId, sensor_type: sensorType, value, unit }),
    }),

  // Alerts & Remedy
  getAlerts: () => request("/alerts"),
  applyRemedy: (alertId) =>
    request(`/alerts/${alertId}/remedy`, {
      method: "POST",
    }),

  // Dashboard Stats
  getDashboardStats: () => request("/dashboard/stats"),

  // ML Disease Prediction
  predictDisease: (file) => {
    const body = new FormData();
    body.append("file", file);
    return request("/ml/predict-disease", {
      method: "POST",
      body,
    });
  },
  predictDiseaseJson: (imageUrl) =>
    request("/ml/predict-disease-json", {
      method: "POST",
      body: JSON.stringify({ image_url: imageUrl }),
    }),
};
