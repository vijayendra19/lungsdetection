import apiClient, { setTokens, clearTokens, getAccessToken } from './api';
import { User, LoginCredentials, RegisterCredentials, AuthTokens } from '../types/auth';

export const authService = {
  async register(credentials: RegisterCredentials): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', credentials);
    return response.data;
  },

  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await apiClient.post<AuthTokens>('/auth/login', credentials);
    const tokens = response.data;
    setTokens(tokens);
    return tokens;
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    localStorage.setItem('steth_user', JSON.stringify(response.data));
    return response.data;
  },

  logout(): void {
    clearTokens();
  },

  isAuthenticated(): boolean {
    return !!getAccessToken();
  },

  getCachedUser(): User | null {
    const userStr = localStorage.getItem('steth_user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },
};

export default authService;
