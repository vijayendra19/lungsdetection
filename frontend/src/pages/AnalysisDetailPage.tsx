import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../services/api';
import reportService from '../services/reportService';
import { 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  FileText, 
  ArrowLeft, 
  ShieldAlert
} from 'lucide-react';

export const AnalysisDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [overlayAlpha, setOverlayAlpha] = useState(0.5);
  const [reportLoading, setReportLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    const fetchAnalysis = async () => {
      try {
        const res = await apiClient.get(`/analysis/${id}`);
        setData(res.data);
      } catch (err) {
        console.error('Failed to load analysis:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalysis();
  }, [id]);

  if (loading) {
    return (
      <div className="py-24 flex flex-col items-center justify-center text-slate-500 gap-3">
        <div className="w-8 h-8 border-2 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
        <span className="text-xs">Loading acoustic analysis...</span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-slate-100">Analysis Record Not Found</h2>
        <p className="text-sm text-slate-400 mt-2 mb-6">The requested screening record could not be loaded.</p>
        <button
          onClick={() => navigate('/history')}
          className="px-5 py-2.5 rounded-xl bg-slate-800 text-slate-200 font-semibold text-sm hover:bg-slate-700"
        >
          Return to History
        </button>
      </div>
    );
  }

  const isNormal = data.classification === 'Normal';

  const handleGenerateReport = async () => {
    setReportLoading(true);
    try {
      const rep = await reportService.generateReport({
        recording_id: data.recording_id,
        analysis_id: data.id,
        report_title: `Cardiopulmonary Screening Report - ${data.file_name}`,
        patient_identifier: `PAT-${data.recording_id.slice(0, 6).toUpperCase()}`,
        primary_diagnosis: data.prediction,
        severity: isNormal ? 'normal' : 'moderate',
        status: 'finalized',
      });
      navigate(`/report/${rep.id}`);
    } catch (err) {
      console.error('Failed to generate report:', err);
    } finally {
      setReportLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/history')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white mb-2 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to History
          </button>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight">
            Auscultation Analysis Detail
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            File: <strong className="text-slate-200">{data.file_name}</strong> • Site: <strong className="text-cyan-400">{data.chest_location}</strong> • Duration: {data.duration_seconds}s
          </p>
        </div>

        <button
          onClick={handleGenerateReport}
          disabled={reportLoading}
          className="inline-flex items-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold text-sm shadow-xl shadow-cyan-500/20 hover:opacity-95 transition-opacity disabled:opacity-50"
        >
          {reportLoading ? (
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          ) : (
            <>
              <FileText className="w-4 h-4" />
              <span>Generate Medical PDF Report</span>
            </>
          )}
        </button>
      </div>

      {/* Primary Diagnosis Banner */}
      <div
        className={`p-6 sm:p-8 rounded-3xl border shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6 ${
          isNormal
            ? 'bg-emerald-950/30 border-emerald-500/30 shadow-emerald-950/20'
            : 'bg-rose-950/30 border-rose-500/30 shadow-rose-950/20'
        }`}
      >
        <div className="flex items-start gap-4">
          <div
            className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 shadow-lg ${
              isNormal
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
            }`}
          >
            {isNormal ? (
              <CheckCircle2 className="w-8 h-8" />
            ) : (
              <ShieldAlert className="w-8 h-8" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span
                className={`text-xs font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                  isNormal
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : 'bg-rose-500/20 text-rose-300'
                }`}
              >
                {data.classification} Finding
              </span>
              <span className="text-xs text-slate-400">• Quality: {data.quality}</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
              {data.prediction}
            </h2>
          </div>
        </div>

        {/* Confidence Gauge */}
        <div className="w-full md:w-auto bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex md:flex-col items-center justify-between md:justify-center gap-2 shrink-0 min-w-[180px]">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Confidence</span>
          <div className="text-3xl font-black text-cyan-400">
            {(data.confidence * 100).toFixed(1)}%
          </div>
          <span className="text-[10px] text-slate-500">Latency: {data.inference_time_ms} ms</span>
        </div>
      </div>

      {/* Clinical Explanation Card */}
      {data.clinical_explanation && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-2">
            Clinical Auscultation Saliency & Acoustic Interpretation
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed">
            {data.clinical_explanation}
          </p>
        </div>
      )}

      {/* Visual Diagnostic Evidence: Spectrogram & Grad-CAM */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <Layers className="w-5 h-5 text-cyan-400" />
              Mel-Spectrogram & Grad-CAM Visual Saliency
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Heatmap highlights the exact acoustic frequencies (20–2000 Hz) that triggered the AI diagnosis.
            </p>
          </div>

          {/* Opacity Control */}
          <div className="flex items-center gap-3 bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 self-start sm:self-auto">
            <span className="text-xs font-medium text-slate-400">Grad-CAM Overlay:</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={overlayAlpha}
              onChange={(e) => setOverlayAlpha(parseFloat(e.target.value))}
              className="w-24 accent-cyan-500 cursor-pointer"
            />
            <span className="text-xs font-bold text-cyan-400 w-8">
              {Math.round(overlayAlpha * 100)}%
            </span>
          </div>
        </div>

        {/* Dual Visualizer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.spectrogram_image && (
            <div className="bg-slate-950 rounded-2xl p-3 border border-slate-800 flex flex-col">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2 px-1">
                <span className="font-semibold">Log Mel-Spectrogram (Cleaned)</span>
                <span>Magma Colormap</span>
              </div>
              <div className="rounded-xl overflow-hidden bg-black flex items-center justify-center aspect-[2/1]">
                <img
                  src={data.spectrogram_image}
                  alt="Mel Spectrogram"
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}

          {data.gradcam_image && (
            <div className="bg-slate-950 rounded-2xl p-3 border border-slate-800 flex flex-col">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2 px-1">
                <span className="font-semibold text-cyan-400">Grad-CAM Decision Map</span>
                <span>Jet Heatmap Saliency</span>
              </div>
              <div className="rounded-xl overflow-hidden bg-black flex items-center justify-center aspect-[2/1] relative">
                <img
                  src={data.gradcam_image}
                  alt="Grad-CAM Saliency Map"
                  className="w-full h-full object-contain"
                  style={{ opacity: 0.3 + overlayAlpha * 0.7 }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
};
