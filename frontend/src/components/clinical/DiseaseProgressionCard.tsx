import React from 'react';
import { DiseaseProgression } from '../../types/audio';
import { 
  AlertTriangle, 
  Stethoscope, 
  Activity, 
  CheckCircle2, 
  ClipboardList, 
  ShieldAlert 
} from 'lucide-react';

interface DiseaseProgressionCardProps {
  prediction: string;
  classification: string;
  category: string;
  progression?: DiseaseProgression;
}

export const DiseaseProgressionCard: React.FC<DiseaseProgressionCardProps> = ({
  prediction,
  classification,
  category,
  progression,
}) => {
  const isNormal = classification === 'Normal' || prediction.toLowerCase().includes('normal');

  // Fallback progression generator if not passed directly from backend
  const data: DiseaseProgression = progression || {
    has_abnormality: !isNormal,
    primary_condition: isNormal ? 'Normal Physiological State' : `Auscultation Anomaly (${prediction})`,
    potential_diseases: isNormal
      ? []
      : [
          category === 'heart' ? 'Valvular Heart Disease' : 'Obstructive Airway Disease',
          category === 'heart' ? 'Ventricular Hypertrophy' : 'Pulmonary Parenchymal Infiltration',
          'Cardiopulmonary Hemodynamic Strain',
        ],
    progression_risks: isNormal
      ? 'Acoustic profile demonstrates regular physiological rhythms without structural valvular or airway remodeling.'
      : 'Unaddressed acoustic abnormalities can progress to worsening structural cardiac remodeling, decompensated heart failure, or respiratory failure.',
    recommended_workup: isNormal
      ? ['Routine annual wellness examination']
      : [
          category === 'heart'
            ? '2D Transthoracic Echocardiogram (TTE) with Doppler'
            : 'Spirometry / Pulmonary Function Testing (PFTs)',
          '12-Lead Electrocardiogram (ECG) / Chest Radiograph',
          'Serum Biomarkers (NT-proBNP / Troponin / CBC)',
          'Specialist Consultation (Cardiology / Pulmonology)',
        ],
    urgency: isNormal ? 'Low (Routine Baseline)' : 'High Priority (Clinical Referral Recommended)',
  };

  if (isNormal) {
    return (
      <div className="bg-white border border-emerald-200/80 rounded-3xl p-6 sm:p-8 shadow-sm space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-600 border border-emerald-200 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-black text-blue-950">Cardiopulmonary Health Assessment</h3>
            <p className="text-xs text-slate-500">Normal Acoustic Parameters & Minimal Disease Risk</p>
          </div>
        </div>

        <div className="p-4 bg-emerald-50/60 rounded-2xl border border-emerald-100 text-sm text-emerald-950 leading-relaxed font-medium">
          {data.progression_risks}
        </div>

        <div className="pt-2 flex items-center justify-between text-xs text-slate-500">
          <span>Clinical Status: <strong className="text-emerald-700 font-bold">Physiologically Normal</strong></span>
          <span>Recommended Follow-up: <strong className="text-blue-950 font-bold">Annual Wellness Checkup</strong></span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border-2 border-rose-200/90 rounded-3xl p-6 sm:p-8 shadow-sm space-y-6">
      
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-rose-50 text-rose-600 border border-rose-200 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-rose-600 uppercase tracking-wider">
                Clinical Differential & Pathological Progression
              </span>
            </div>
            <h3 className="text-xl font-black text-blue-950 mt-0.5">
              What This Abnormality Leads To & Associated Diseases
            </h3>
          </div>
        </div>

        {/* Urgency Badge */}
        <div className="self-start sm:self-auto px-3.5 py-1.5 rounded-full bg-rose-100 text-rose-800 text-xs font-extrabold border border-rose-300 flex items-center gap-1.5 shadow-sm">
          <AlertTriangle className="w-4 h-4 text-rose-600" />
          <span>{data.urgency}</span>
        </div>
      </div>

      {/* Primary Correlation & Potential Disease Differentials */}
      <div className="space-y-3">
        <div className="text-xs font-extrabold text-blue-900 uppercase tracking-wider flex items-center gap-1.5">
          <Stethoscope className="w-4 h-4 text-blue-600" />
          <span>Potential Diagnoses & Associated Conditions:</span>
        </div>

        <div className="flex flex-wrap gap-2">
          {data.potential_diseases.map((dis, idx) => (
            <div
              key={idx}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-50 border border-blue-200 text-blue-950 text-xs font-bold shadow-sm"
            >
              <div className="w-2 h-2 rounded-full bg-blue-600" />
              <span>{dis}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Progression Risks If Untreated */}
      <div className="p-4 bg-rose-50/70 rounded-2xl border border-rose-200 space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold text-rose-800 uppercase tracking-wider">
          <Activity className="w-4 h-4 text-rose-600" />
          <span>Disease Progression & Pathological Complications (If Untreated):</span>
        </div>
        <p className="text-sm text-rose-950 font-medium leading-relaxed">
          {data.progression_risks}
        </p>
      </div>

      {/* Recommended Clinical Diagnostic Workup */}
      <div className="space-y-3">
        <div className="text-xs font-extrabold text-blue-900 uppercase tracking-wider flex items-center gap-1.5">
          <ClipboardList className="w-4 h-4 text-blue-600" />
          <span>Recommended Next Diagnostic Workup:</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {data.recommended_workup.map((item, idx) => (
            <div
              key={idx}
              className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-start gap-2.5 text-xs text-blue-950 font-semibold shadow-sm"
            >
              <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};

export default DiseaseProgressionCard;
