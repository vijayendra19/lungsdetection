import { DiseaseProgression } from './audio';

export interface ClinicalReport {
  id: string;
  user_id: string;
  recording_id: string;
  analysis_id: string;
  report_title: string;
  patient_identifier: string;
  primary_diagnosis: string;
  severity: string;
  clinical_summary: string;
  clinical_explanation?: string;
  disease_progression?: DiseaseProgression;
  recommendations?: string;
  status: string;
  sound_category?: string;
  chest_location?: string;
  confidence?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateReportPayload {
  recording_id: string;
  analysis_id: string;
  report_title?: string;
  patient_identifier?: string;
  primary_diagnosis?: string;
  severity?: string;
  clinical_summary?: string;
  recommendations?: string;
  status?: string;
}
