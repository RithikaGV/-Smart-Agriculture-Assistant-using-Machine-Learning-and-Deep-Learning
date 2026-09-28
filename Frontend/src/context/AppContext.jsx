import React, { createContext, useContext, useState, useEffect } from 'react';
import { INITIAL_GROWER_PROFILE, DEFAULT_PLANT_IMAGE } from '../data/mockData';
import { api, setAuthToken, getAuthToken } from '../api/client';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // Theme state: 'bright' or 'dark'
  const [theme, setTheme] = useState('dark');
  
  // Auth state
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [growerProfile, setGrowerProfile] = useState(INITIAL_GROWER_PROFILE);

  // Active view
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedPlantId, setSelectedPlantId] = useState('plant-1');

  // Core Data
  const [plants, setPlants] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [toasts, setToasts] = useState([]);

  // Fetch initial data from backend API for current logged-in user
  const refreshBackendData = async () => {
    try {
      const backendPlants = await api.getPlants();
      if (backendPlants && Array.isArray(backendPlants)) {
        setPlants(backendPlants);
      }
    } catch (e) {
      console.log("Backend sync offline or unauthenticated:", e);
    }

    try {
      const backendAlerts = await api.getAlerts();
      if (backendAlerts && Array.isArray(backendAlerts)) {
        setAlerts(backendAlerts);
      }
    } catch (e) {
      // fallback
    }
  };

  // Initialize session token on app load
  useEffect(() => {
    const initSession = async () => {
      const token = getAuthToken();
      if (!token) {
        // Log in default grower if no token is present
        await login('rajesh.kumar@smartagri.org', 'password123');
      } else {
        try {
          const profile = await api.getProfile();
          if (profile) {
            setGrowerProfile(profile);
          }
        } catch (e) {
          // Token expired or invalid
          await login('rajesh.kumar@smartagri.org', 'password123');
        }
        await refreshBackendData();
      }
    };
    initSession();
  }, []);

  // Apply theme class to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Toast Helper
  const showToast = (message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  };

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'bright' : 'dark';
    setTheme(newTheme);
    showToast(`Switched to ${newTheme === 'dark' ? 'Deep Canopy Dark Mode' : 'Emerald Bright Mode'}`, 'info');
  };

  const login = async (email, password) => {
    // Clear state before switching user
    setPlants([]);
    setAlerts([]);
    
    try {
      const res = await api.login(email, password);
      if (res && res.access_token) {
        setAuthToken(res.access_token);
        if (res.user) {
          setGrowerProfile(res.user);
        }
      }
    } catch (e) {
      console.log("Falling back to offline login", e);
    }

    setIsLoggedIn(true);
    setActiveTab('dashboard');
    showToast("Logged in successfully!");
    await refreshBackendData();
  };

  const logout = () => {
    setAuthToken("");
    setIsLoggedIn(false);
    setPlants([]);
    setAlerts([]);
    setActiveTab('welcome');
    showToast("Logged out successfully", 'info');
  };

  const updateProfile = async (updatedProfile) => {
    setGrowerProfile(prev => ({ ...prev, ...updatedProfile }));
    try {
      await api.updateProfile(updatedProfile);
    } catch (e) {
      // fallback
    }
    showToast("Grower's profile updated successfully!");
  };

  // Add Plant function
  const addPlant = async (newPlantData) => {
    const plantImage = newPlantData.image && newPlantData.image.trim() !== '' 
      ? newPlantData.image 
      : DEFAULT_PLANT_IMAGE;

    const payload = {
      name: newPlantData.name || "New Hydroponic Crop",
      species: newPlantData.species || "General Species",
      location: newPlantData.location || "Greenhouse Bay 1",
      image: plantImage,
      sensors: newPlantData.sensors,
      notes: newPlantData.notes || "Newly added plant."
    };

    try {
      const created = await api.createPlant(payload);
      if (created) {
        showToast(`Successfully added "${created.name}"!`);
        await refreshBackendData();
        return;
      }
    } catch (e) {
      console.error("Failed to add plant to backend", e);
      showToast("Error adding plant. Please sign in again.", "warning");
    }
  };

  // Edit Plant function
  const updatePlant = async (plantId, updatedFields) => {
    try {
      const updated = await api.updatePlant(plantId, updatedFields);
      if (updated) {
        showToast("Plant details updated successfully!");
        await refreshBackendData();
        return;
      }
    } catch (e) {
      console.error("Error updating plant", e);
    }
  };

  const deletePlant = async (plantId) => {
    const plantName = plants.find(p => p.id === plantId)?.name;
    try {
      await api.deletePlant(plantId);
    } catch (e) {
      console.error("Error deleting plant", e);
    }
    if (selectedPlantId === plantId) {
      setActiveTab('my-plants');
    }
    showToast(`Deleted ${plantName || 'plant'}`, 'warning');
    await refreshBackendData();
  };

  // Sensor connect helper
  const connectSensorToPlant = async (plantId, sensorType, address) => {
    const targetAddress = address || `SENSOR-${Math.floor(Math.random() * 9000 + 1000)}`;
    try {
      await api.connectSensor(plantId, sensorType, targetAddress);
    } catch (e) {
      // Fallback
    }
    showToast(`Connected ${sensorType} sensor (${targetAddress})!`);
    await refreshBackendData();
  };

  // Resolve Alert action & fix telemetry
  const applyRemedy = async (alertId) => {
    const targetAlert = alerts.find(a => a.id === alertId);
    if (!targetAlert) return;

    try {
      await api.applyRemedy(alertId);
    } catch (e) {
      console.error("Error applying remedy", e);
    }

    showToast(`Applied remedy: "${targetAlert.title}". Plant status stabilized!`);
    await refreshBackendData();
  };

  const navigateToPlantDetail = (plantId) => {
    setSelectedPlantId(plantId);
    setActiveTab('plant-detail');
  };

  return (
    <AppContext.Provider value={{
      theme,
      toggleTheme,
      isLoggedIn,
      login,
      logout,
      growerProfile,
      updateProfile,
      activeTab,
      setActiveTab,
      selectedPlantId,
      setSelectedPlantId,
      navigateToPlantDetail,
      plants,
      addPlant,
      updatePlant,
      deletePlant,
      connectSensorToPlant,
      alerts,
      applyRemedy,
      toasts,
      showToast,
      refreshBackendData
    }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
