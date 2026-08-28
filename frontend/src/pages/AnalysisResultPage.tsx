import React, { useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { AudioAnalysisResult } from '../types/audio';
import reportService from '../services/reportService';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';
import { 
  CheckCircle2, 
  AlertTriangle,
  FileText, 
  ArrowLeft, 
  Volume2, 
  BarChart3, 
  ShieldAlert, 
  Sparkles, 
  X, 
  Sliders, 
  ChevronDown, 
  ChevronUp, 
  Heart, 
  Wind 
} from 'lucide-react';

export const AnalysisResultPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const result = location.state?.result as AudioAnalysisResult | undefined;
  const fileName = location.state?.file_name || 'Stethoscope Recording';
  const chestLocation = location.state?.chest_location || 'Apex';

  const [overlayAlpha, setOverlayAlpha] = useState(0.55);
  const [showGradcamModal, setShowGradcamModal] = useState(false);
  const [showExplainDetails, setShowExplainDetails] = useState(true);
  const [reportLoading, setReportLoading] = useState(false);

  if (!result) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-slate-100">No Analysis Result Loaded</h2>
        <p className="text-sm text-slate-400 mt-2 mb-6">Please upload or record an audio file to view screening results.</p>
        <Link
          to="/analyze"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 text-white font-semibold text-sm"
        >
          New Analysis
        </Link>
      </div>
    );
  }

  const isNormal = result.classification === 'Normal';

  // Format waveform for Recharts
  const waveformChartData = (result.waveform_data || []).map((val, idx) => {
    const totalPoints = result.waveform_data.length;
    const timeSec = ((idx / totalPoints) * 5.0).toFixed(2);
    return {
      time: `${timeSec}s`,
      amplitude: val,
    };
  });

  const handleGenerateReport = async () => {
    setReportLoading(true);
    try {
      const rep = await reportService.generateReport({
        recording_id: result.recording_id,
        analysis_id: result.recording_id,
        report_title: `Cardiopulmonary Screening Report - ${fileName}`,
        patient_identifier: `PAT-${result.recording_id.slice(0, 6).toUpperCase()}`,
        primary_diagnosis: result.prediction,
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
      
      {/* Top Navigation & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white mb-2 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight">
            AI Screening Diagnosis
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            File: <strong className="text-slate-200">{fileName}</strong> • Site: <strong className="text-cyan-400">{chestLocation}</strong>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* "Why this prediction?" Button */}
          <button
            type="button"
            onClick={() => setShowGradcamModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500/20 to-rose-500/20 hover:from-amber-500/30 hover:to-rose-500/30 border border-amber-500/30 text-amber-300 font-bold text-xs shadow-lg shadow-amber-500/10 transition-all active:scale-95"
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Why this prediction?</span>
          </button>

          {/* Medical Report CTA */}
          <button
            onClick={handleGenerateReport}
            disabled={reportLoading}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold text-xs shadow-xl shadow-cyan-500/20 hover:opacity-95 transition-opacity disabled:opacity-50"
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
      </div>

      {/* Primary Diagnosis & Quality Banner */}
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
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <span
                className={`text-xs font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                  isNormal
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                }`}
              >
                {result.classification} Finding
              </span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 capitalize flex items-center gap-1">
                {result.category === 'heart' ? <Heart className="w-3 h-3 text-rose-400" /> : <Wind className="w-3 h-3 text-cyan-400" />}
                {result.category}
              </span>
              <span className="text-xs text-slate-400">
                • Quality: <strong className="text-slate-200">{result.quality}</strong>
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white mt-1">
              {result.prediction}
            </h2>
          </div>
        </div>

        {/* AI Confidence Meter */}
        <div className="w-full md:w-auto bg-slate-900/90 border border-slate-800 rounded-2xl p-4 flex md:flex-col items-center justify-between md:justify-center gap-2 shrink-0 min-w-[180px]">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Confidence</span>
          <div className="text-3xl font-black text-cyan-400">
            {(result.confidence * 100).toFixed(1)}%
          </div>
          <span className="text-[10px] text-slate-500">
            {result.inference_time_ms ? `Latency: ${result.inference_time_ms} ms` : 'Neural Network Softmax'}
          </span>
        </div>
      </div>

      {/* "Why this prediction?" Explainability Section */}
      <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">Why this prediction?</h3>
              <p className="text-xs text-slate-400">Acoustic Grad-CAM Saliency Analysis & Plain-Language Explanation</p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setShowExplainDetails(!showExplainDetails)}
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
          >
            <span>{showExplainDetails ? 'Hide Saliency View' : 'Show Saliency View'}</span>
            {showExplainDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        {showExplainDetails && (
          <div className="pt-4 border-t border-slate-800/80 space-y-6">
            
            {/* Plain-Language Clinical Explanation Box */}
            <div className="p-4 bg-slate-950/80 rounded-2xl border border-slate-800/80 text-sm text-slate-300 leading-relaxed">
              <p className="font-semibold text-cyan-400 mb-1 text-xs uppercase tracking-wider">
                Clinical Acoustic Summary:
              </p>
              {isNormal ? (
                <span>
                  The neural network analyzed the frequency spectrum and identified standard physiological acoustic rhythms with clear, 
                  well-defined S1 and S2 heart sounds or laminar respiratory breath phases. No anomalous energy spikes or pathological murmurs were detected.
                </span>
              ) : (
                <span>
                  The neural network detected anomalous high-energy acoustic turbulence localized in the frequency range highlighted in the 
                  Grad-CAM heatmap below. The temporal cadence and frequency profile correspond to characteristic features of 
                  <strong className="text-white"> {result.prediction}</strong>.
                </span>
              )}
            </div>

            {/* Visual Spectrogram & Grad-CAM Side-by-Side */}
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Grad-CAM Saliency Map vs. Mel-Spectrogram
                </span>
                
                {/* Opacity Control */}
                <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 self-start sm:self-auto">
                  <Sliders className="w-3.5 h-3.5 text-slate-400" />
                  <span className="text-xs text-slate-400">Heatmap Blend:</span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={overlayAlpha}
                    onChange={(e) => setOverlayAlpha(parseFloat(e.target.value))}
                    className="w-20 accent-cyan-500 cursor-pointer"
                  />
                  <span className="text-xs font-bold text-cyan-400 w-8">
                    {Math.round(overlayAlpha * 100)}%
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Clean Mel-Spectrogram */}
                <div className="bg-slate-950 rounded-2xl p-3 border border-slate-800 flex flex-col">
                  <div className="flex justify-between text-xs text-slate-400 mb-2 px-1">
                    <span className="font-semibold">Log Mel-Spectrogram</span>
                    <span>20 – 2000 Hz</span>
                  </div>
                  <div className="rounded-xl overflow-hidden bg-black flex items-center justify-center aspect-[2/1]">
                    <img
                      src={result.spectrogram_image}
                      alt="Mel Spectrogram"
                      className="w-full h-full object-contain"
                    />
                  </div>
                </div>

                {/* Grad-CAM Overlay */}
                <div className="bg-slate-950 rounded-2xl p-3 border border-slate-800 flex flex-col">
                  <div className="flex justify-between text-xs text-slate-400 mb-2 px-1">
                    <span className="font-semibold text-amber-400">Grad-CAM Neural Saliency</span>
                    <span className="text-rose-400 font-bold">Red = Diagnostic Trigger</span>
                  </div>
                  <div className="rounded-xl overflow-hidden bg-black flex items-center justify-center aspect-[2/1]">
                    <img
                      src={result.gradcam_image}
                      alt="Grad-CAM Saliency Map"
                      className="w-full h-full object-contain"
                      style={{ opacity: 0.3 + overlayAlpha * 0.7 }}
                    />
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>

      {/* Waveform Chart (Recharts) & Class Probabilities Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Recharts Waveform Visualizer */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 mb-1">
              <Volume2 className="w-4 h-4 text-cyan-400" />
              Preprocessed Acoustic Waveform
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Recharts time-series amplitude graph (Butterworth filtered 20–1800 Hz).
            </p>
          </div>

          <div className="h-48 w-full bg-slate-950 rounded-2xl border border-slate-800 p-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={waveformChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="waveGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#475569" tick={{ fontSize: 10 }} interval={Math.floor(waveformChartData.length / 5)} />
                <YAxis stroke="#475569" tick={{ fontSize: 10 }} domain={[-1, 1]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.75rem',
                    fontSize: '12px',
                    color: '#f8fafc',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="amplitude"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#waveGradient)"
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Neural Network Probability Distribution */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 mb-1">
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              Class Probabilities
            </h3>
            <p className="text-xs text-slate-400 mb-4">Neural Softmax Output</p>

            <div className="space-y-3">
              {result.class_probabilities &&
                Object.entries(result.class_probabilities).map(([cls, prob]) => (
                  <div key={cls}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-medium text-slate-300 truncate max-w-[160px]">{cls}</span>
                      <span className="font-bold text-cyan-400">{(prob * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full transition-all duration-500"
                        style={{ width: `${prob * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
            <span>Primary Category</span>
            <strong className="text-slate-300 uppercase">{result.category}</strong>
          </div>
        </div>

      </div>

      {/* Modal: Full-Screen Grad-CAM Explainability Inspection */}
      {showGradcamModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-3xl w-full p-6 sm:p-8 shadow-2xl space-y-6 relative max-h-[90vh] overflow-y-auto">
            
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <Sparkles className="w-5 h-5 text-amber-400" />
                <h3 className="text-lg font-bold text-slate-100">Grad-CAM Neural Saliency Details</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowGradcamModal(false)}
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <p className="text-sm text-slate-300 leading-relaxed">
                Gradient-weighted Class Activation Mapping (Grad-CAM) calculates the gradient of the 
                <strong className="text-cyan-400"> {result.prediction}</strong> score with respect to the convolutional feature maps.
                The highlighted red and yellow bands pinpoint the precise acoustic temporal pulses and frequencies that triggered this diagnosis.
              </p>

              <div className="bg-slate-950 rounded-2xl p-4 border border-slate-800">
                <img
                  src={result.gradcam_image}
                  alt="Full Saliency Map"
                  className="w-full rounded-xl object-contain"
                />
              </div>

              <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800/80 text-xs text-slate-400 space-y-1">
                <div>• <strong>Primary Class:</strong> {result.prediction}</div>
                <div>• <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%</div>
                <div>• <strong>Site:</strong> {chestLocation}</div>
                <div>• <strong>Frequency Envelope:</strong> 20 Hz to 2000 Hz Butterworth Bandpass</div>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowGradcamModal(false)}
                className="px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs transition-colors"
              >
                Close Saliency Inspector
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
