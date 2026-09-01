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

  async downloadReportPdf(id: string, filename?: string): Promise<void> {
    const response = await apiClient.get(`/report/${id}?format=pdf`, {
      responseType: 'blob',
    });

    const blob = new Blob([response.data], { type: 'application/pdf' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || `clinical_report_${id.slice(0, 8)}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  },

  getReportPdfUrl(id: string): string {
    const token = localStorage.getItem('steth_access_token');
    return `/api/report/${id}/pdf${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  },
};

export default reportService;
