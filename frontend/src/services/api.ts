import axios, { AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import toast from 'react-hot-toast';
import type {
  User,
  AuthTokens,
  LoginRequest,
  RegisterRequest,
  UpdateProfileRequest,
  Quiz,
  QuizDetail,
  StartQuizRequest,
  QuizSession,
  Question,
  SubmitAnswerRequest,
  AnswerResponse,
  SessionResults,
  Leaderboard,
  ApiError,
} from '@/types';

// Extend InternalAxiosRequestConfig to include _retry property
interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

// Create axios instance
const api = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
const TOKEN_KEY = 'quiz_access_token';
const REFRESH_TOKEN_KEY = 'quiz_refresh_token';

export const getAccessToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const setTokens = (tokens: AuthTokens): void => {
  localStorage.setItem(TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
};

export const clearTokens = (): void => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as CustomAxiosRequestConfig | undefined;

    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;

      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          const response = await axios.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          });

          const tokens: AuthTokens = response.data;
          setTokens(tokens);

          // Retry original request
          original.headers.Authorization = `Bearer ${tokens.access_token}`;
          return axios(original);
        } catch (refreshError) {
          clearTokens();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        clearTokens();
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Error handler
const handleApiError = (error: AxiosError): never => {
  let message = 'An unexpected error occurred';

  if (error.response?.data) {
    const errorData = error.response.data as ApiError;
    message = errorData.detail || message;
  } else if (error.request) {
    message = 'Network error. Please check your connection.';
  } else {
    message = error.message;
  }

  toast.error(message);
  throw new Error(message);
};

// API methods
export const authApi = {
  register: async (data: RegisterRequest): Promise<User> => {
    try {
      const response: AxiosResponse<User> = await api.post('/auth/register', data);
      toast.success('Account created successfully!');
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  login: async (data: LoginRequest): Promise<AuthTokens> => {
    try {
      const response: AxiosResponse<AuthTokens> = await api.post('/auth/login', data);
      setTokens(response.data);
      toast.success('Logged in successfully!');
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  logout: async (): Promise<void> => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearTokens();
      toast.success('Logged out successfully!');
    }
  },

  getProfile: async (): Promise<User> => {
    try {
      const response: AxiosResponse<User> = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  updateProfile: async (data: UpdateProfileRequest): Promise<User> => {
    try {
      const response: AxiosResponse<User> = await api.patch('/auth/me', data);
      toast.success('Profile updated successfully!');
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  refreshToken: async (): Promise<AuthTokens> => {
    try {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response: AxiosResponse<AuthTokens> = await api.post('/auth/refresh', {
        refresh_token: refreshToken,
      });

      setTokens(response.data);
      return response.data;
    } catch (error) {
      clearTokens();
      return handleApiError(error as AxiosError);
    }
  },
};

export const quizApi = {
  getQuizzes: async (params?: {
    topic?: string;
    difficulty?: string;
    limit?: number;
    offset?: number;
  }): Promise<Quiz[]> => {
    try {
      const response: AxiosResponse<Quiz[]> = await api.get('/quizzes', { params });
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  getQuizDetail: async (quizId: string): Promise<QuizDetail> => {
    try {
      const response: AxiosResponse<QuizDetail> = await api.get(`/quizzes/${quizId}`);
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  startQuiz: async (quizId: string, data: StartQuizRequest): Promise<QuizSession> => {
    try {
      const response: AxiosResponse<QuizSession> = await api.post(
        `/quizzes/${quizId}/start`,
        data
      );
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  getQuestion: async (sessionId: string, questionIndex: number): Promise<Question> => {
    try {
      const response: AxiosResponse<Question> = await api.get(
        `/quizzes/sessions/${sessionId}/question/${questionIndex}`
      );
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  submitAnswer: async (
    sessionId: string,
    data: SubmitAnswerRequest
  ): Promise<AnswerResponse> => {
    try {
      const response: AxiosResponse<AnswerResponse> = await api.post(
        `/quizzes/sessions/${sessionId}/answer`,
        data
      );
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  finishSession: async (sessionId: string): Promise<SessionResults> => {
    try {
      const response: AxiosResponse<SessionResults> = await api.post(
        `/quizzes/sessions/${sessionId}/finish`
      );
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  getSessionResults: async (sessionId: string): Promise<SessionResults> => {
    try {
      const response: AxiosResponse<SessionResults> = await api.get(
        `/quizzes/sessions/${sessionId}/results`
      );
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },

  getLeaderboard: async (params?: {
    topic?: string;
    limit?: number;
  }): Promise<Leaderboard> => {
    try {
      const response: AxiosResponse<Leaderboard> = await api.get('/quizzes/leaderboard', {
        params,
      });
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },
};

// Health check
export const healthCheck = async (): Promise<boolean> => {
  try {
    await axios.get('/health');
    return true;
  } catch (error) {
    return false;
  }
};

// Unified API service object
export const apiService = {
  // Auth methods
  login: authApi.login,
  register: authApi.register,
  logout: authApi.logout,
  getProfile: authApi.getProfile,
  updateProfile: authApi.updateProfile,

  // Quiz methods
  getQuizzes: quizApi.getQuizzes,
  getQuiz: quizApi.getQuizDetail,
  startQuizSession: (quizId: string, requestData: StartQuizRequest) =>
    quizApi.startQuiz(quizId, requestData),
  getQuestion: async (sessionId: string, questionIndex: number) => {
    try {
      const response: AxiosResponse<Question> = await api.get(`/quizzes/sessions/${sessionId}/question/${questionIndex}`);
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },
  submitAnswer: async (sessionId: string, data: SubmitAnswerRequest) => {
    try {
      const response: AxiosResponse<AnswerResponse> = await api.post(`/quizzes/sessions/${sessionId}/answer`, data);
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },
  finishSession: async (sessionId: string) => {
    try {
      const response: AxiosResponse<SessionResults> = await api.post(`/quizzes/sessions/${sessionId}/finish`);
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },
  getSessionResults: async (sessionId: string) => {
    try {
      const response: AxiosResponse<SessionResults> = await api.get(`/quizzes/sessions/${sessionId}/results`);
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },
  getLeaderboard: async (topic?: string) => {
    try {
      const params = topic ? { topic } : {};
      const response: AxiosResponse<Leaderboard> = await api.get('/quizzes/leaderboard', { params });
      return response.data;
    } catch (error) {
      return handleApiError(error as AxiosError);
    }
  },
};

export default api;