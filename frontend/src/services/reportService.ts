import apiClient from './api';
import { ClinicalReport, CreateReportPayload } from '../types/report';

export const reportService = {
  async generateReport(payload: CreateReportPayload): Promise<ClinicalReport> {
    const response = await apiClient.post<ClinicalReport>('/report/generate', payload);
    return response.data;
  },

  async getReport(id: string): Promise<ClinicalReport> {
    const response = await apiClient.get<ClinicalReport>(`/report/${id}`);
    return response.data;
  },

  getReportPdfUrl(id: string): string {
    return `/api/report/${id}/pdf`;
  },
};

export default reportService;
