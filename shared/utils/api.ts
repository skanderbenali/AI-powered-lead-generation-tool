/**
 * API client utilities for making requests to the backend
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API client configuration
interface ApiClientConfig {
  baseURL: string;
  timeout?: number;
  headers?: Record<string, string>;
}

// Default API configuration
const defaultConfig: ApiClientConfig = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * API client for making requests to the backend
 */
export class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(config: ApiClientConfig = defaultConfig) {
    this.client = axios.create(config);
    
    // Add request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers['Authorization'] = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle API errors here
        if (error.response) {
          // Server responded with a status code outside the 2xx range
          if (error.response.status === 401) {
            // Unauthorized - token expired or invalid
            this.clearToken();
            // Redirect to login if needed
            if (typeof window !== 'undefined') {
              window.location.href = '/auth/login';
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Set authentication token
   */
  setToken(token: string): void {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  /**
   * Get current authentication token
   */
  getToken(): string | null {
    if (!this.token && typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
    return this.token;
  }

  /**
   * Clear authentication token
   */
  clearToken(): void {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Get request
   */
  async get<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.get<T>(url, config);
  }

  /**
   * Post request
   */
  async post<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.post<T>(url, data, config);
  }

  /**
   * Put request
   */
  async put<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.put<T>(url, data, config);
  }

  /**
   * Patch request
   */
  async patch<T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.patch<T>(url, data, config);
  }

  /**
   * Delete request
   */
  async delete<T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<T>> {
    return this.client.delete<T>(url, config);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// API endpoints
export const endpoints = {
  auth: {
    login: '/auth/login',
    register: '/auth/register',
  },
  leads: {
    list: '/leads',
    search: '/leads/search',
    detail: (id: number) => `/leads/${id}`,
    enrich: (id: number) => `/leads/${id}/enrich`,
  },
  projects: {
    list: '/projects',
    detail: (id: number) => `/projects/${id}`,
    stats: (id: number) => `/projects/${id}/stats`,
  },
  emails: {
    templates: '/emails/templates',
    templateDetail: (id: number) => `/emails/templates/${id}`,
    campaigns: '/emails/campaigns',
    campaignDetail: (id: number) => `/emails/campaigns/${id}`,
    startCampaign: (id: number) => `/emails/campaigns/${id}/start`,
  },
  ai: {
    generateEmail: '/ai/generate-email',
    predictEmail: '/ai/predict-email',
    scoreLeads: '/ai/score-leads',
  },
  analytics: {
    dashboard: '/analytics/dashboard',
    leadQuality: '/analytics/leads/quality',
    campaignPerformance: '/analytics/campaigns/performance',
  },
};
