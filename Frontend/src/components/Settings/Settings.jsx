import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Settings as SettingsIcon, User, Mail, MapPin, Globe, Hash, Lock, ShieldCheck, Sun, Moon, KeyRound, CheckCircle2 } from 'lucide-react';
import './Settings.css';

export const Settings = () => {
  const { growerProfile, updateProfile, theme, toggleTheme, showToast } = useApp();

  const [profileForm, setProfileForm] = useState({
    name: growerProfile.name || '',
    email: growerProfile.email || '',
    address: growerProfile.address || '',
    state: growerProfile.state || '',
    country: growerProfile.country || '',
    pincode: growerProfile.pincode || ''
  });

  // OTP Change Password state
  const [otpStep, setOtpStep] = useState(1); // 1: Send OTP, 2: Enter OTP & New Password, 3: Success
  const [otpCode, setOtpCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');

  const handleProfileChange = (e) => {
    setProfileForm({ ...profileForm, [e.target.name]: e.target.value });
  };

  const handleSaveProfile = (e) => {
    e.preventDefault();
    updateProfile(profileForm);
  };

  const handleSendOtp = () => {
    showToast(`OTP code sent to ${profileForm.email}! (Simulated OTP: 789012)`, 'info');
    setOtpStep(2);
  };

  const handleVerifyPasswordChange = (e) => {
    e.preventDefault();
    if (newPassword !== confirmNewPassword) {
      alert("New passwords do not match!");
      return;
    }
    if (otpCode !== '789012' && otpCode !== '123456') {
      showToast("OTP verified successfully!", 'success');
    }
    setOtpStep(3);
    showToast("Password updated successfully using OTP!");
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <SettingsIcon size={28} />
            Grower Profile & App Settings
          </h1>
          <p className="page-subtitle">
            Configure profile credentials, security password via OTP, and app color schema themes.
          </p>
        </div>
      </div>

      <div className="settings-grid">
        {/* LEFT COLUMN: EDIT THE GROWER'S PROFILE */}
        <div className="glass-card">
          <h2 className="settings-section-title">
            <User size={22} color="var(--accent-emerald)" />
            Edit the Grower's profile
          </h2>

          <form onSubmit={handleSaveProfile} className="auth-form">
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">
                  <User size={16} /> Grower's Name
                </label>
                <input
                  type="text"
                  name="name"
                  className="form-control"
                  value={profileForm.name}
                  onChange={handleProfileChange}
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
                  value={profileForm.email}
                  onChange={handleProfileChange}
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
                value={profileForm.address}
                onChange={handleProfileChange}
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
                  value={profileForm.state}
                  onChange={handleProfileChange}
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
                  value={profileForm.country}
                  onChange={handleProfileChange}
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
                  value={profileForm.pincode}
                  onChange={handleProfileChange}
                  required
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ marginTop: '0.5rem' }}>
              <CheckCircle2 size={18} /> Save Profile Changes
            </button>
          </form>
        </div>

        {/* RIGHT COLUMN: CHANGE PASSWORD USING OTP & THEME SCHEMA */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* CHANGE PASSWORD USING OTP */}
          <div className="glass-card">
            <h2 className="settings-section-title">
              <KeyRound size={22} color="var(--accent-emerald)" />
              Change Password Using OTP
            </h2>

            {otpStep === 1 && (
              <div className="otp-step-box">
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  Click below to generate a secure One-Time Password (OTP) to your registered email: <strong>{profileForm.email}</strong>.
                </p>
                <button type="button" className="btn btn-primary" onClick={handleSendOtp}>
                  <Mail size={16} /> Request Security OTP Code
                </button>
              </div>
            )}

            {otpStep === 2 && (
              <form onSubmit={handleVerifyPasswordChange} className="otp-step-box">
                <div className="form-group">
                  <label className="form-label">Enter 6-Digit OTP Code</label>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="e.g. 789012"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    required
                  />
                </div>

                <div className="grid-2">
                  <div className="form-group">
                    <label className="form-label">New Password</label>
                    <input
                      type="password"
                      className="form-control"
                      placeholder="••••••••"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Confirm New Password</label>
                    <input
                      type="password"
                      className="form-control"
                      placeholder="••••••••"
                      value={confirmNewPassword}
                      onChange={(e) => setConfirmNewPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <button type="submit" className="btn btn-primary">
                  <ShieldCheck size={18} /> Update Password
                </button>
              </form>
            )}

            {otpStep === 3 && (
              <div className="otp-step-box" style={{ textAlign: 'center' }}>
                <CheckCircle2 size={36} color="var(--status-healthy)" style={{ margin: '0 auto' }} />
                <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>Password Changed Successfully!</div>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => setOtpStep(1)}>
                  Reset OTP Flow
                </button>
              </div>
            )}
          </div>

          {/* CHANGE THE SCHEMA (BRIGHT / DARK MODE) */}
          <div className="glass-card">
            <h2 className="settings-section-title">
              <Sun size={22} color="var(--accent-emerald)" />
              Change the Schema (Bright / Dark mode)
            </h2>

            <div className="theme-schema-cards">
              <div
                className={`theme-schema-card ${theme === 'dark' ? 'active' : ''}`}
                onClick={() => { if (theme !== 'dark') toggleTheme(); }}
              >
                <Moon size={28} color="var(--accent-emerald-light)" />
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>Dark Schema</div>
                  <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>Deep Canopy Obsidian</div>
                </div>
              </div>

              <div
                className={`theme-schema-card ${theme === 'bright' ? 'active' : ''}`}
                onClick={() => { if (theme !== 'bright') toggleTheme(); }}
              >
                <Sun size={28} color="var(--status-warning)" />
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>Bright Schema</div>
                  <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>Light Emerald Clean</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
