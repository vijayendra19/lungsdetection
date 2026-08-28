export interface HistoryItem {
  recording_id: string;
  analysis_id?: string;
  date: string;
  category: 'heart' | 'lung' | 'mixed';
  chest_location: string;
  file_name: string;
  duration_seconds: number;
  classification: 'Normal' | 'Abnormal' | 'Unanalyzed';
  prediction: string;
  confidence?: number;
  has_report: boolean;
  patient_gender?: string;
  patient_age?: number;
}

export interface HistoryResponse {
  total: number;
  skip: number;
  limit: number;
  items: HistoryItem[];
}

export interface ScreeningStats {
  total_screenings: number;
  analyzed_count: number;
  normal_findings: number;
  abnormal_findings: number;
  category_distribution: {
    heart: number;
    lung: number;
    mixed: number;
  };
}
