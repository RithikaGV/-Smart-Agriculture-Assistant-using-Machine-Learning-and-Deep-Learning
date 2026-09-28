import React from 'react';
import { useApp, AppProvider } from './context/AppContext';
import { Sidebar } from './components/Sidebar/Sidebar';
import { Navbar } from './components/Navbar/Navbar';
import { ToastContainer } from './components/UI/Toast';
import { Login } from './components/Auth/Login';
import { Signup } from './components/Auth/Signup';
import { Dashboard } from './components/Dashboard/Dashboard';
import { MyPlants } from './components/Plants/MyPlants';
import { PlantDetail } from './components/Plants/PlantDetail';
import { Alerts } from './components/Alerts/Alerts';
import { DiseaseDetection } from './components/DiseaseDetection/DiseaseDetection';
import { Settings } from './components/Settings/Settings';

const MainAppContent = () => {
  const { isLoggedIn, activeTab } = useApp();

  if (activeTab === 'signup') {
    return <Signup />;
  }

  if (!isLoggedIn || activeTab === 'welcome') {
    return <Login />;
  }

  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-content-wrapper">
        <Navbar />
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'my-plants' && <MyPlants />}
        {activeTab === 'plant-detail' && <PlantDetail />}
        {activeTab === 'alerts' && <Alerts />}
        {activeTab === 'disease-detection' && <DiseaseDetection />}
        {activeTab === 'settings' && <Settings />}
      </div>
      <ToastContainer />
    </div>
  );
};

export default function App() {
  return (
    <AppProvider>
      <MainAppContent />
    </AppProvider>
  );
}
