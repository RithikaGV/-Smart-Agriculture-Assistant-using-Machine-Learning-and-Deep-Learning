import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Cpu, User, Mail, MapPin, Globe, Hash, Lock, CheckCircle2 } from 'lucide-react';
import './Auth.css';

export const Signup = () => {
  const { login, updateProfile, setActiveTab } = useApp();
  const [formData, setFormData] = useState({
    name: 'Dr. Rajesh Kumar',
    email: 'rajesh.kumar@smartagri.org',
    address: 'Plot 42, Agritech Innovation Hub',
    state: 'Karnataka',
    country: 'India',
    pincode: '560100',
    password: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.password && formData.password !== formData.confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    updateProfile({
      name: formData.name,
      email: formData.email,
      address: formData.address,
      state: formData.state,
      country: formData.country,
      pincode: formData.pincode
    });
    login(formData.email, formData.password);
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card" style={{ maxWidth: '580px' }}>
        <div className="auth-header">
          <div className="auth-logo">
            <Cpu size={32} />
          </div>
          <h1 className="auth-title">ACCOUNT CREATION</h1>
          <p className="auth-subtitle">Register your Smart Agriculture IoT Profile</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">
                <User size={16} /> Grower's Name
              </label>
              <input
                type="text"
                name="name"
                className="form-control"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <Mail size={16} /> Email Id
              </label>
              <input
                type="email"
                name="email"
                className="form-control"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">
              <MapPin size={16} /> Address
            </label>
            <input
              type="text"
              name="address"
              className="form-control"
              value={formData.address}
              onChange={handleChange}
              required
            />
          </div>

          <div className="grid-3">
            <div className="form-group">
              <label className="form-label">State</label>
              <input
                type="text"
                name="state"
                className="form-control"
                value={formData.state}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <Globe size={16} /> Country
              </label>
              <input
                type="text"
                name="country"
                className="form-control"
                value={formData.country}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <Hash size={16} /> Pincode
              </label>
              <input
                type="text"
                name="pincode"
                className="form-control"
                value={formData.pincode}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">
                <Lock size={16} /> Password
              </label>
              <input
                type="password"
                name="password"
                className="form-control"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <Lock size={16} /> Confirm Password
              </label>
              <input
                type="password"
                name="confirmPassword"
                className="form-control"
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
            <CheckCircle2 size={18} /> Create Account
          </button>
        </form>

        <div className="auth-footer-link">
          <span>Already registered?</span>
          <span className="auth-link" onClick={() => setActiveTab('welcome')}>
            Back to Welcome Page
          </span>
        </div>
      </div>
    </div>
  );
};
