import axios from 'axios';
import { VerificationResult } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export const verifyFlyer = async (file: File): Promise<VerificationResult> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post<VerificationResult>('/verify', formData);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Verification failed');
    } else if (error.request) {
      throw new Error('Unable to connect to server. Please ensure the backend is running.');
    } else {
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
};

export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get('/health');
    return response.data.status === 'healthy';
  } catch {
    return false;
  }
};

