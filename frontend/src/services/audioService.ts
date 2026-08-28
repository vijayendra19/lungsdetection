import apiClient from './api';
import { AudioAnalysisResult, RecordingMetadata } from '../types/audio';

export const audioService = {
  async uploadAudio(formData: FormData): Promise<RecordingMetadata> {
    const response = await apiClient.post<RecordingMetadata>('/audio/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async analyzeAudio(formData: FormData): Promise<AudioAnalysisResult> {
    const response = await apiClient.post<AudioAnalysisResult>('/audio/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getRecording(id: string): Promise<RecordingMetadata> {
    const response = await apiClient.get<RecordingMetadata>(`/audio/${id}`);
    return response.data;
  },

  getAudioStreamUrl(id: string): string {
    return `/api/audio/${id}/file`;
  },
};

export default audioService;
