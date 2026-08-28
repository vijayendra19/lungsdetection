import apiClient from './api';
import { HistoryResponse, ScreeningStats } from '../types/history';

export const historyService = {
  async getHistory(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    classification?: string;
  }): Promise<HistoryResponse> {
    const response = await apiClient.get<HistoryResponse>('/history/', { params });
    return response.data;
  },

  async getStats(): Promise<ScreeningStats> {
    const response = await apiClient.get<ScreeningStats>('/history/stats');
    return response.data;
  },
};

export default historyService;
