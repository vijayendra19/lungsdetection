import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { usePWAInstall } from '../../hooks/usePWAInstall';
import { 
  Activity, 
  UploadCloud, 
  History, 
  LogOut, 
  ShieldCheck,
  Download
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { isInstallable, installPWA } = usePWAInstall();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <Activity className="w-6 h-6 text-white animate-pulse-subtle" />
            </div>
            <div>
              <span className="font-bold text-lg text-blue-950 tracking-tight">Smart Stethoscope</span>
              <span className="text-xs font-semibold px-2 py-0.5 ml-2 rounded-full bg-blue-50 text-blue-700 border border-blue-200">AI PWA</span>
            </div>
          </Link>

          {/* Navigation Links */}
          {user && (
            <nav className="hidden md:flex items-center gap-1">
              <Link
                to="/dashboard"
                className={`px-3.5 py-2 rounded-lg text-sm font-semibold transition-colors ${
                  isActive('/dashboard')
                    ? 'bg-blue-50 text-blue-700 border border-blue-200/80 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-blue-900'
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/analyze"
                className={`px-3.5 py-2 rounded-lg text-sm font-semibold flex items-center gap-1.5 transition-colors ${
                  isActive('/analyze')
                    ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/20'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-blue-900'
                }`}
              >
                <UploadCloud className="w-4 h-4" />
                New Analysis
              </Link>
              <Link
                to="/history"
                className={`px-3.5 py-2 rounded-lg text-sm font-semibold flex items-center gap-1.5 transition-colors ${
                  isActive('/history')
                    ? 'bg-blue-50 text-blue-700 border border-blue-200/80 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-blue-900'
                }`}
              >
                <History className="w-4 h-4" />
                History
              </Link>
            </nav>
          )}

          {/* User Profile & Actions */}
          <div className="flex items-center gap-3">
            {/* PWA Install Button */}
            {isInstallable && (
              <button
                type="button"
                onClick={installPWA}
                className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 border border-blue-200 text-blue-700 text-xs font-bold transition-all shadow-sm"
                title="Install Progressive Web App on your device"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Install App</span>
              </button>
            )}

            {user ? (
              <div className="flex items-center gap-3">
                <div className="hidden sm:flex flex-col text-right">
                  <span className="text-sm font-bold text-blue-950">{user.full_name}</span>
                  <span className="text-xs text-emerald-600 font-semibold flex items-center justify-end gap-1">
                    <ShieldCheck className="w-3 h-3" />
                    {user.role}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 rounded-lg bg-slate-100 text-slate-500 hover:text-rose-600 hover:bg-rose-50 border border-slate-200 transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-lg text-sm font-semibold text-slate-700 hover:text-blue-900 hover:bg-slate-100 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-lg text-sm font-bold bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20 hover:opacity-95 transition-opacity"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

        </div>
      </div>
    </header>
  );
};
