// API Types
export interface User {
  id: string;
  email: string;
  display_name: string | null;
  mobile_number: string | null;
  role: 'user' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string;
  mobile_number?: string;
}

export interface UpdateProfileRequest {
  display_name?: string;
  mobile_number?: string;
}

// Quiz Types
export interface Quiz {
  id: string;
  title: string;
  description: string | null;
  total_questions: number;
  topics: string[];
  difficulties: string[];
  estimated_time_minutes: number;
}

export interface QuizDetail extends Quiz {
  question_breakdown: Record<string, number>;
  topic_breakdown: Record<string, number>;
}

export interface StartQuizRequest {
  num_questions: number;
  difficulty_mix?: Record<string, number>;
  topics?: string[];
  seed?: number;
  participant_name: string;
  participant_mobile: string;
}

export interface QuizSession {
  session_id: string;
  started_at: string;
  expires_at: string;
  questions_count: number;
  first_question_index: number;
  topics: string[];
  difficulty_distribution: Record<string, number>;
  seed?: number;
}

export interface Question {
  index: number;
  question_id: string;
  question_text: string;
  options: Record<string, string>;
  topic: string;
  difficulty: string;
  time_limit_seconds: number;  // Each question has a time limit (default 60 seconds)
}

export interface SubmitAnswerRequest {
  question_id: string;
  selected_option: string;
  time_taken_ms: number;
}

export interface AnswerResponse {
  question_id: string;
  is_correct: boolean;
  current_score: number;
  total_answered: number;
}

export interface QuizResult {
  question_id: string;
  question_text: string;
  selected_option: string | null;  // null if question was skipped
  correct_option: string;
  is_correct: boolean;
  explanation?: string;
  time_taken_ms: number;
  topic: string;
  difficulty: string;
}

export interface SessionResults {
  session_id: string;
  score: number;
  total_questions: number;
  percentage: number;
  time_taken_seconds: number;
  started_at: string;
  finished_at: string;
  results: QuizResult[];
  performance_by_topic: Record<string, { correct: number; total: number }>;
  performance_by_difficulty: Record<string, { correct: number; total: number }>;
}

export interface LeaderboardEntry {
  rank: number;
  display_name: string;
  participant_mobile?: string;
  score: number;
  total_questions: number;
  percentage: number;
  time_taken_seconds: number;
  created_at: string;
  is_current_user: boolean;
}

export interface Leaderboard {
  entries: LeaderboardEntry[];
  total_entries: number;
  current_user_rank?: number;
  filters: Record<string, string | null>;
}

// UI Types
export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string | null;
}

export interface QuizState {
  currentQuestion: Question | null;
  currentQuestionIndex: number;
  session: QuizSession | null;
  answers: Record<string, string>;
  timeSpent: Record<string, number>;
  isSubmitting: boolean;
  isFinished: boolean;
}

export type Difficulty = 'easy' | 'medium' | 'hard';

export type QuizStatus = 'not-started' | 'in-progress' | 'completed' | 'expired';

// Component Props Types
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  description?: string;
}

export interface ProgressProps {
  value: number;
  max: number;
  className?: string;
  showLabel?: boolean;
}