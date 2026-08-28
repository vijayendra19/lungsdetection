import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import historyService from '../services/historyService';
import { ScreeningStats, HistoryItem } from '../types/history';
import { 
  Activity, 
  Heart, 
  Wind, 
  UploadCloud, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  FileText,
  Clock,
  Sparkles,
  Layers
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<ScreeningStats | null>(null);
  const [recentItems, setRecentItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [statsData, historyData] = await Promise.all([
          historyService.getStats(),
          historyService.getHistory({ limit: 6 }),
        ]);
        setStats(statsData);
        setRecentItems(historyData.items);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboardData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Prominent CTA Hero Banner */}
      <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/60 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl">
        <div className="absolute -right-16 -bottom-16 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        
        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold mb-4">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Smart Stethoscope AI Screening v1.0</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight leading-tight">
              Welcome, {user?.full_name || 'Clinician'}
            </h1>
            <p className="text-sm sm:text-base text-slate-300 mt-2 leading-relaxed">
              Screen digital stethoscope audio for heart murmurs, gallops, crackles, and wheezes with instant 
              <strong className="text-cyan-400 font-semibold"> Mel-Spectrograms</strong> and 
              <strong className="text-cyan-400 font-semibold"> Grad-CAM Neural Saliency</strong> explainability.
            </p>
          </div>

          {/* Prominent "Analyze New Recording" CTA */}
          <Link
            to="/analyze"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-extrabold text-base shadow-2xl shadow-cyan-500/30 hover:opacity-95 hover:scale-[1.02] active:scale-[0.98] transition-all group shrink-0"
          >
            <UploadCloud className="w-6 h-6 group-hover:animate-bounce" />
            <span>Analyze New Recording</span>
            <ArrowRight className="w-5 h-5 ml-1" />
          </Link>
        </div>
      </div>

      {/* Summary Metrics Cards (Total, Normal, Abnormal) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        
        {/* Total Analyses */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl backdrop-blur-sm relative overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Analyses</span>
            <div className="w-11 h-11 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
              <Activity className="w-5 h-5" />
            </div>
          </div>
          <div className="text-4xl font-black text-slate-100">{stats?.total_screenings ?? 0}</div>
          <div className="text-xs text-slate-400 mt-2 flex items-center gap-2">
            <span className="text-cyan-400 font-semibold">{stats?.analyzed_count ?? 0} analyzed</span>
            <span>•</span>
            <span>Recorded stethoscope sessions</span>
          </div>
        </div>

        {/* Normal Count */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl backdrop-blur-sm relative overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Normal Findings</span>
            <div className="w-11 h-11 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="text-4xl font-black text-emerald-400">{stats?.normal_findings ?? 0}</div>
          <div className="text-xs text-slate-400 mt-2">
            Normal physiological rhythm & laminar breath sounds
          </div>
        </div>

        {/* Abnormal Count */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl backdrop-blur-sm relative overflow-hidden sm:col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Abnormal Findings</span>
            <div className="w-11 h-11 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-4xl font-black text-amber-400">{stats?.abnormal_findings ?? 0}</div>
          <div className="text-xs text-slate-400 mt-2">
            Cardiac murmurs, adventitious lung crackles / wheezing
          </div>
        </div>

      </div>

      {/* Recent Screening Activity */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-slate-100">Recent Screening History</h2>
            <p className="text-xs text-slate-400 mt-0.5">Most recent acoustic auscultation records</p>
          </div>
          <Link
            to="/history"
            className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 py-2 px-3.5 rounded-xl hover:bg-slate-800/80 transition-colors"
          >
            <span>All Records</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="py-16 flex flex-col items-center justify-center text-slate-500 gap-3">
            <div className="w-8 h-8 border-2 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
            <span className="text-xs">Loading records...</span>
          </div>
        ) : recentItems.length === 0 ? (
          <div className="py-16 text-center border-2 border-dashed border-slate-800/80 rounded-2xl">
            <Activity className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h3 className="text-base font-bold text-slate-300">No screenings recorded yet</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto mb-5">
              Upload a .wav stethoscope audio file or record live using your microphone to begin.
            </p>
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 text-xs font-bold px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/20 hover:opacity-95 transition-opacity"
            >
              <UploadCloud className="w-4 h-4" />
              Analyze First Recording
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentItems.map((item) => (
              <div
                key={item.recording_id}
                className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 hover:border-slate-700 transition-all flex flex-col justify-between gap-4"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                        item.classification === 'Normal'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}
                    >
                      {item.classification}
                    </span>
                    <span className="text-[11px] text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(item.date).toLocaleDateString()}
                    </span>
                  </div>

                  <h3 className="font-bold text-sm text-slate-100 truncate mb-1">
                    {item.prediction || item.file_name}
                  </h3>

                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    {item.category === 'heart' ? (
                      <span className="flex items-center gap-1 text-rose-400">
                        <Heart className="w-3.5 h-3.5" /> Heart
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-cyan-400">
                        <Wind className="w-3.5 h-3.5" /> Lung
                      </span>
                    )}
                    <span>•</span>
                    <span>Site: <strong className="text-slate-300">{item.chest_location}</strong></span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-800/80">
                  <span className="text-xs text-cyan-400 font-semibold">
                    {item.confidence ? `${(item.confidence * 100).toFixed(1)}% confidence` : 'Processed'}
                  </span>
                  
                  <div className="flex items-center gap-1.5">
                    {item.analysis_id && (
                      <Link
                        to={`/analysis/${item.analysis_id}`}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors"
                        title="View Visual Analysis"
                      >
                        <Layers className="w-4 h-4" />
                      </Link>
                    )}
                    {item.has_report && (
                      <Link
                        to={`/report/${item.analysis_id}`}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-cyan-500/10 text-slate-400 hover:text-cyan-400 transition-colors"
                        title="Medical Report"
                      >
                        <FileText className="w-4 h-4" />
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};
