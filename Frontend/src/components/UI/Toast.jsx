import React from 'react';
import { useApp } from '../../context/AppContext';
import { CheckCircle2, AlertTriangle, AlertCircle, Info } from 'lucide-react';

export const ToastContainer = () => {
  const { toasts } = useApp();

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map(toast => {
        let Icon = CheckCircle2;
        let colorClass = 'var(--status-healthy)';

        if (toast.type === 'warning') {
          Icon = AlertTriangle;
          colorClass = 'var(--status-warning)';
        } else if (toast.type === 'danger' || toast.type === 'critical') {
          Icon = AlertCircle;
          colorClass = 'var(--status-critical)';
        } else if (toast.type === 'info') {
          Icon = Info;
          colorClass = 'var(--accent-emerald)';
        }

        return (
          <div key={toast.id} className="toast">
            <Icon size={20} color={colorClass} />
            <span>{toast.message}</span>
          </div>
        );
      })}
    </div>
  );
};
