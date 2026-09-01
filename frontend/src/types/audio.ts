export interface DiseaseProgression {
  has_abnormality: boolean;
  primary_condition: string;
  potential_diseases: string[];
  progression_risks: string;
  recommended_workup: string[];
  urgency: string;
}

export interface AudioAnalysisResult {
  recording_id: string;
  quality: string;
  category: 'heart' | 'lung' | 'mixed';
  classification: 'Normal' | 'Abnormal';
  prediction: string;
  confidence: number;
  waveform_data: number[];
  spectrogram_image: string;
  gradcam_image: string;
  class_probabilities?: Record<string, number>;
  inference_time_ms?: number;
  clinical_explanation?: string;
  disease_progression?: DiseaseProgression;
}

export interface RecordingMetadata {
  id: string;
  user_id: string;
  sound_category: string;
  chest_location: string;
  file_path: string;
  file_name: string;
  duration_seconds: number;
  sample_rate: number;
  channels: number;
  patient_gender?: string;
  patient_age?: number;
  clinical_notes?: string;
  recorded_at: string;
  created_at: string;
}
