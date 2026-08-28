import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import reportService from '../services/reportService';
import { ClinicalReport } from '../types/report';
import { 
  FileText, 
  Download, 
  ArrowLeft, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  ShieldCheck,
  RotateCcw,
  Layers,
  Heart,
  Wind
} from 'lucide-react';

export const ReportViewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [report, setReport] = useState<ClinicalReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await reportService.getReport(id);
      setReport(data);
    } catch (err: any) {
      console.error('Failed to load report:', err);
      setError(err.response?.data?.detail || 'Failed to retrieve clinical report from server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [id]);

  if (loading) {
    return (
      <div className="py-28 flex flex-col items-center justify-center text-slate-500 gap-3">
        <div className="w-10 h-10 border-3 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
        <span className="text-sm font-medium text-slate-400">Compiling official clinical report document...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-rose-400 mx-auto" />
        <h2 className="text-xl font-bold text-slate-100">Unable to Load Medical Report</h2>
        <p className="text-sm text-slate-400 max-w-md mx-auto">{error}</p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            onClick={fetchReport}
            className="px-4 py-2 rounded-xl bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 text-xs font-bold hover:bg-cyan-500/20 transition-colors flex items-center gap-1.5"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
          <button
            onClick={() => navigate('/history')}
            className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-bold transition-colors"
          >
            Return to History
          </button>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto" />
        <h2 className="text-xl font-bold text-slate-100">Medical Report Not Found</h2>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          The requested clinical screening report could not be found or has been archived.
        </p>
        <button
          onClick={() => navigate('/history')}
          className="px-5 py-2.5 rounded-xl bg-slate-800 text-slate-200 font-semibold text-sm hover:bg-slate-700 transition-colors"
        >
          Return to History
        </button>
      </div>
    );
  }

  const isNormal = (report.primary_diagnosis || '').toLowerCase().includes('normal');
  const pdfUrl = id ? reportService.getReportPdfUrl(id) : '#';

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Navigation & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/history')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white mb-2 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Screening History
          </button>
          <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight flex items-center gap-2.5">
            <FileText className="w-6 h-6 text-cyan-400" />
            Clinical Auscultation Report
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Report ID: <span className="font-mono text-slate-300">{report.id}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          {report.analysis_id && (
            <Link
              to={`/analysis/${report.analysis_id}`}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-colors"
            >
              <Layers className="w-4 h-4 text-cyan-400" />
              <span>Inspect Saliency</span>
            </Link>
          )}

          <a
            href={pdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 hover:opacity-95 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download Printable PDF</span>
          </a>
        </div>
      </div>

      {/* Rendered Clinical Report Document */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
        
        {/* Document Header Banner */}
        <div className="flex flex-col sm:flex-row justify-between items-start pb-6 border-b border-slate-800 gap-4">
          <div>
            <span className="text-xs font-bold text-cyan-400 tracking-wider uppercase">
              Smart Stethoscope AI Screening
            </span>
            <h2 className="text-xl font-bold text-slate-100 mt-1">{report.report_title}</h2>
          </div>
          <div className="text-xs text-slate-400 text-left sm:text-right space-y-1">
            <div className="flex items-center gap-1.5 sm:justify-end">
              <Clock className="w-3.5 h-3.5" />
              <span>{new Date(report.created_at).toLocaleString()}</span>
            </div>
            <span className="inline-block px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-semibold uppercase text-[10px]">
              Status: {report.status}
            </span>
          </div>
        </div>

        {/* Patient & Exam Metadata */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-slate-950/60 rounded-2xl border border-slate-800/80">
          <div>
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Patient ID</span>
            <div className="text-sm font-bold text-slate-200 mt-0.5">{report.patient_identifier}</div>
          </div>
          <div>
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Auscultation Site</span>
            <div className="text-sm font-bold text-cyan-400 mt-0.5">{report.chest_location || 'Apex'}</div>
          </div>
          <div>
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Sound Domain</span>
            <div className="text-sm font-bold text-slate-200 mt-0.5 capitalize flex items-center gap-1">
              {report.sound_category === 'heart' ? <Heart className="w-3.5 h-3.5 text-rose-400" /> : <Wind className="w-3.5 h-3.5 text-cyan-400" />}
              {report.sound_category || 'Heart'}
            </div>
          </div>
          <div>
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Severity Flag</span>
            <div className="text-sm font-bold text-slate-200 mt-0.5 capitalize">{report.severity}</div>
          </div>
        </div>

        {/* Diagnosis Outcome Box */}
        <div
          className={`p-5 rounded-2xl border flex items-start gap-4 ${
            isNormal
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300'
              : 'bg-rose-500/10 border-rose-500/20 text-rose-300'
          }`}
        >
          {isNormal ? (
            <CheckCircle2 className="w-7 h-7 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-7 h-7 text-rose-400 shrink-0 mt-0.5" />
          )}
          <div>
            <div className="text-xs font-bold uppercase tracking-wider">Primary Diagnosis</div>
            <div className="text-xl font-black text-white mt-0.5">{report.primary_diagnosis}</div>
            {report.confidence && (
              <div className="text-xs text-slate-400 mt-1">
                Neural Confidence Rating: <strong className="text-cyan-400">{(report.confidence * 100).toFixed(1)}%</strong>
              </div>
            )}
          </div>
        </div>

        {/* Clinical Plain-Language Explanation */}
        <div>
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Clinical Explanation & Acoustic Findings
          </h3>
          <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 text-sm text-slate-300 leading-relaxed">
            {report.clinical_explanation || report.clinical_summary}
          </div>
        </div>

        {/* Recommendations */}
        {report.recommendations && (
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Actionable Recommendations
            </h3>
            <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 text-sm text-slate-300 space-y-1">
              {report.recommendations.split('\n').map((line, idx) => (
                <p key={idx}>{line}</p>
              ))}
            </div>
          </div>
        )}

        {/* Medical Disclaimer */}
        <div className="pt-4 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-start gap-2">
          <ShieldCheck className="w-4 h-4 shrink-0 text-slate-600 mt-0.5" />
          <span>
            <strong>Clinical Notice:</strong> This report is generated by an assistive AI model for decision support.
            It must be interpreted by a qualified medical professional alongside full patient clinical history and diagnostic workup.
          </span>
        </div>

      </div>

    </div>
  );
};
