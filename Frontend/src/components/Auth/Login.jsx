import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import { Cpu, Mail, Lock, ArrowRight, UserCheck } from 'lucide-react';
import './Auth.css';

export const Login = () => {
  const { login, setActiveTab, growerProfile } = useApp();
  const [email, setEmail] = useState(growerProfile.email || '');
  const [password, setPassword] = useState('password123');

  const handleSubmit = (e) => {
    e.preventDefault();
    login(email, password);
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <Cpu size={32} />
          </div>
          <h1 className="auth-title">WELCOME PAGE</h1>
          <p className="auth-subtitle">Sign in to your Smart Agriculture & IoT Portal</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">
              <Mail size={16} /> Enter Email ID
            </label>
            <input
              type="email"
              className="form-control"
              placeholder="e.g. grower@smartagri.org"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <Lock size={16} /> Password
            </label>
            <input
              type="password"
              className="form-control"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '0.5rem' }}>
            Sign In <ArrowRight size={18} />
          </button>
        </form>

        <div className="auth-footer-link">
          <span>No account?</span>
          <span className="auth-link" onClick={() => setActiveTab('signup')}>
            Create a new one
          </span>
        </div>

        <div className="demo-login-box">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => login('demo@smartagri.org', 'demo')}
            style={{ width: '100%' }}
          >
            <UserCheck size={16} /> Quick Demo Login as Grower
          </button>
        </div>
      </div>
    </div>
  );
};
