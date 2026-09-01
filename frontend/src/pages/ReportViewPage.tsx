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
import { DiseaseProgressionCard } from '../components/clinical/DiseaseProgressionCard';

export const ReportViewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [report, setReport] = useState<ClinicalReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
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

  const handleDownloadPdf = async () => {
    if (!id) return;
    setDownloadingPdf(true);
    try {
      const filename = `clinical_report_${report?.patient_identifier || id.slice(0, 8)}.pdf`;
      await reportService.downloadReportPdf(id, filename);
    } catch (err: any) {
      console.error('PDF download error:', err);
      alert('Failed to download PDF: ' + (err.response?.data?.detail || err.message));
    } finally {
      setDownloadingPdf(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [id]);

  if (loading) {
    return (
      <div className="py-28 flex flex-col items-center justify-center text-slate-400 gap-3 bg-slate-50 min-h-[calc(100vh-4rem)]">
        <div className="w-10 h-10 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        <span className="text-sm font-bold text-blue-950">Compiling official clinical report document...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-4 bg-slate-50">
        <AlertTriangle className="w-12 h-12 text-rose-500 mx-auto" />
        <h2 className="text-xl font-bold text-blue-950">Unable to Load Medical Report</h2>
        <p className="text-sm text-slate-500 max-w-md mx-auto">{error}</p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            onClick={fetchReport}
            className="px-4 py-2 rounded-xl bg-blue-50 text-blue-700 border border-blue-200 text-xs font-bold hover:bg-blue-100 transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Retry</span>
          </button>
          <button
            onClick={() => navigate('/history')}
            className="px-4 py-2 rounded-xl bg-slate-200 text-slate-700 hover:bg-slate-300 text-xs font-bold transition-colors cursor-pointer"
          >
            Return to History
          </button>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center space-y-4 bg-slate-50">
        <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto" />
        <h2 className="text-xl font-bold text-blue-950">Medical Report Not Found</h2>
        <p className="text-sm text-slate-500 max-w-md mx-auto">
          The requested clinical screening report could not be found or has been archived.
        </p>
        <button
          onClick={() => navigate('/history')}
          className="px-5 py-2.5 rounded-xl bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 transition-colors cursor-pointer"
        >
          Return to History
        </button>
      </div>
    );
  }

  const isNormal = (report.primary_diagnosis || '').toLowerCase().includes('normal');

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 bg-slate-50">
      
      {/* Navigation & Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/history')}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-500 hover:text-blue-900 mb-2 transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Screening History
          </button>
          <h1 className="text-2xl font-black text-blue-950 tracking-tight flex items-center gap-2.5">
            <FileText className="w-6 h-6 text-blue-600" />
            Clinical Auscultation Report
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Report ID: <span className="font-mono text-blue-950 font-bold">{report.id}</span>
          </p>
        </div>

        <div className="flex items-center gap-3">
          {report.analysis_id && (
            <Link
              to={`/analysis/${report.analysis_id}`}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-white border border-slate-200 hover:bg-blue-50 text-blue-700 text-xs font-bold shadow-sm transition-colors"
            >
              <Layers className="w-4 h-4 text-blue-600" />
              <span>Inspect Saliency</span>
            </Link>
          )}

          <button
            onClick={handleDownloadPdf}
            disabled={downloadingPdf}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-xs shadow-md shadow-blue-500/20 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 transition-all cursor-pointer"
          >
            {downloadingPdf ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Generating PDF...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Download Printable PDF</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Rendered Clinical Report Document (Clean White Medical Paper Style) */}
      <div className="bg-white border border-slate-200/90 rounded-3xl p-6 sm:p-8 shadow-sm space-y-6">
        
        {/* Document Header Banner */}
        <div className="flex flex-col sm:flex-row justify-between items-start pb-6 border-b border-slate-200 gap-4">
          <div>
            <span className="text-xs font-bold text-blue-700 tracking-wider uppercase">
              Smart Stethoscope AI Screening
            </span>
            <h2 className="text-xl font-black text-blue-950 mt-1">{report.report_title}</h2>
          </div>
          <div className="text-xs text-slate-500 text-left sm:text-right space-y-1">
            <div className="flex items-center gap-1.5 sm:justify-end font-medium">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span>{new Date(report.created_at).toLocaleString()}</span>
            </div>
            <span className="inline-block px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 font-bold uppercase text-[10px] border border-slate-200">
              Status: {report.status}
            </span>
          </div>
        </div>

        {/* Patient & Exam Metadata */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-slate-50/80 rounded-2xl border border-slate-200">
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Patient ID</span>
            <div className="text-sm font-extrabold text-blue-950 mt-0.5">{report.patient_identifier}</div>
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Auscultation Site</span>
            <div className="text-sm font-extrabold text-blue-600 mt-0.5">{report.chest_location || 'Apex'}</div>
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Sound Domain</span>
            <div className="text-sm font-extrabold text-blue-950 mt-0.5 capitalize flex items-center gap-1">
              {report.sound_category === 'heart' ? <Heart className="w-3.5 h-3.5 text-rose-500" /> : <Wind className="w-3.5 h-3.5 text-blue-500" />}
              {report.sound_category || 'Heart'}
            </div>
          </div>
          <div>
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Severity Flag</span>
            <div className="text-sm font-extrabold text-blue-950 mt-0.5 capitalize">{report.severity}</div>
          </div>
        </div>

        {/* Diagnosis Outcome Box (Green for Normal, Red for Abnormal) */}
        <div
          className={`p-5 rounded-2xl border flex items-start gap-4 ${
            isNormal
              ? 'bg-emerald-50 border-emerald-200 text-emerald-950'
              : 'bg-rose-50 border-rose-200 text-rose-950'
          }`}
        >
          {isNormal ? (
            <CheckCircle2 className="w-7 h-7 text-emerald-600 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-7 h-7 text-rose-600 shrink-0 mt-0.5" />
          )}
          <div>
            <div className={`text-xs font-bold uppercase tracking-wider ${isNormal ? 'text-emerald-800' : 'text-rose-800'}`}>Primary Diagnosis</div>
            <div className="text-xl font-black text-blue-950 mt-0.5">{report.primary_diagnosis}</div>
            {report.confidence && (
              <div className="text-xs text-slate-600 mt-1 font-medium">
                Neural Confidence Rating: <strong className={isNormal ? 'text-emerald-700' : 'text-rose-700'}>{(report.confidence * 100).toFixed(1)}%</strong>
              </div>
            )}
          </div>
        </div>

        {/* Clinical Plain-Language Explanation */}
        <div>
          <h3 className="text-xs font-bold text-blue-950 uppercase tracking-wider mb-2">
            Clinical Explanation & Acoustic Findings
          </h3>
          <div className="p-4 bg-blue-50/60 rounded-2xl border border-blue-100 text-sm text-blue-950 leading-relaxed font-medium">
            {report.clinical_explanation || report.clinical_summary}
          </div>
        </div>

        {/* Disease Progression & Differential Diagnoses */}
        <DiseaseProgressionCard
          prediction={report.primary_diagnosis}
          classification={isNormal ? 'Normal' : 'Abnormal'}
          category={report.sound_category || 'heart'}
          progression={report.disease_progression}
        />

        {/* Recommendations */}
        {report.recommendations && (
          <div>
            <h3 className="text-xs font-bold text-blue-950 uppercase tracking-wider mb-2">
              Actionable Recommendations
            </h3>
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 text-sm text-slate-700 space-y-1 font-medium">
              {report.recommendations.split('\n').map((line, idx) => (
                <p key={idx}>{line}</p>
              ))}
            </div>
          </div>
        )}

        {/* Medical Disclaimer */}
        <div className="pt-4 border-t border-slate-200 text-[11px] text-slate-500 flex items-start gap-2">
          <ShieldCheck className="w-4 h-4 shrink-0 text-slate-400 mt-0.5" />
          <span>
            <strong>Clinical Notice:</strong> This report is generated by an assistive AI model for decision support.
            It must be interpreted by a qualified medical professional alongside full patient clinical history and diagnostic workup.
          </span>
        </div>

      </div>

    </div>
  );
};

export default ReportViewPage;
