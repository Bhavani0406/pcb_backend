import { create } from 'zustand';

// URL helper to automatically resolve backend endpoints
const BACKEND_BASE = 'localhost:8000';
export const API_URL = `http://${BACKEND_BASE}`;
export const WS_URL = `ws://${BACKEND_BASE}`;

export interface MCQOption {
  id: string;
  text: string;
}

export interface MCQQuestion {
  id: string;
  question: string;
  difficulty: string;
  topic: string;
  options: MCQOption[];
  difficulty_weight?: number;
  tags: string[];
}

export interface MCQAnswerResponse {
  question_id: string;
  selected_option: string;
  correct_option: string;
  is_correct: boolean;
  explanation: string;
  engineering_reasoning: string;
}

export interface VoiceEvaluation {
  question: string;
  transcribed_answer: string;
  technical_analysis: {
    correctness: number;
    technical_depth: number;
    problem_solving: number;
    communication: number;
    practical_understanding: number;
  };
  strengths: string[];
  weaknesses: string[];
  ideal_answer: string;
  engineering_explanation: string;
  feedback: string;
  score: number;
  confidence_score: number;
}

export interface VoiceSessionSummary {
  session_id: string;
  total_questions: number;
  overall_score: number;
  technical_depth_avg: number;
  problem_solving_avg: number;
  communication_avg: number;
  practical_understanding_avg: number;
  topic_scores: Record<string, number>;
  feedback_summary: string;
  recommendations: string[];
}

export interface MCQSessionSummary {
  session_id: string;
  total_questions: number;
  correct_answers: number;
  score_percentage: number;
  analytics: {
    feedback: string;
    strengths: string[];
    weaknesses: string[];
  };
}

interface AppState {
  session_id: string | null;
  interview_type: 'mcq' | 'voice' | null;
  difficulty: string;
  topic: string;
  style: string;
  current_view: 'dashboard' | 'mcq' | 'voice' | 'summary';
  
  // MCQ state
  mcq_questions: MCQQuestion[];
  current_mcq_index: number;
  mcq_answers: Record<string, MCQAnswerResponse>;
  mcq_summary: MCQSessionSummary | null;
  
  // Voice state
  voice_question: string | null;
  voice_audio: string | null;
  voice_evaluations: VoiceEvaluation[];
  voice_summary: VoiceSessionSummary | null;
  transcription: string;
  is_recording: boolean;
  websocket: WebSocket | null;
  
  // UI state
  loading: boolean;
  error: string | null;

  // Actions
  setDifficulty: (diff: string) => void;
  setTopic: (topic: string) => void;
  setStyle: (style: string) => void;
  setView: (view: 'dashboard' | 'mcq' | 'voice' | 'summary') => void;
  setRecording: (recording: boolean) => void;
  setTranscription: (text: string) => void;
  setError: (err: string | null) => void;
  
  // Session routines
  initMCQSession: () => Promise<void>;
  submitMCQAnswer: (questionId: string, selectedOption: string) => Promise<void>;
  finishMCQSession: () => Promise<void>;
  
  initVoiceSession: () => Promise<void>;
  connectVoiceWebSocket: () => void;
  submitVoiceAnswer: (transcript: string) => void;
  finishVoiceSession: () => Promise<void>;
  resetSession: () => void;
}

export const useAppStore = create<AppState>((set, get) => ({
  session_id: null,
  interview_type: null,
  difficulty: 'medium',
  topic: 'General Hardware Design',
  style: 'General Panel',
  current_view: 'dashboard',
  
  mcq_questions: [],
  current_mcq_index: 0,
  mcq_answers: {},
  mcq_summary: null,
  
  voice_question: null,
  voice_audio: null,
  voice_evaluations: [],
  voice_summary: null,
  transcription: '',
  is_recording: false,
  websocket: null,
  
  loading: false,
  error: null,

  setDifficulty: (difficulty) => set({ difficulty }),
  setTopic: (topic) => set({ topic }),
  setStyle: (style) => set({ style }),
  setView: (current_view) => set({ current_view }),
  setRecording: (is_recording) => set({ is_recording }),
  setTranscription: (transcription) => set({ transcription }),
  setError: (error) => set({ error }),

  initMCQSession: async () => {
    set({ loading: true, error: null, interview_type: 'mcq' });
    try {
      const response = await fetch(`${API_URL}/api/mcq/init`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          difficulty: get().difficulty,
          topic: get().topic,
          style: get().style
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to initialize MCQ session. Check if backend is running.');
      }
      
      const data = await response.json();
      set({
        session_id: data.session_id,
        mcq_questions: data.questions,
        current_mcq_index: 0,
        mcq_answers: {},
        current_view: 'mcq',
        loading: false
      });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  submitMCQAnswer: async (questionId, selectedOption) => {
    const sessionId = get().session_id;
    if (!sessionId) return;
    
    set({ loading: true });
    try {
      const response = await fetch(`${API_URL}/api/mcq/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          question_id: questionId,
          selected_option: selectedOption
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit MCQ answer.');
      }
      
      const data = await response.json();
      set((state) => ({
        mcq_answers: { ...state.mcq_answers, [questionId]: data },
        loading: false
      }));
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  finishMCQSession: async () => {
    const sessionId = get().session_id;
    if (!sessionId) return;
    
    set({ loading: true });
    try {
      const response = await fetch(`${API_URL}/api/mcq/summary/${sessionId}`);
      if (!response.ok) {
        throw new Error('Failed to load MCQ session summary.');
      }
      const data = await response.json();
      set({
        mcq_summary: data,
        current_view: 'summary',
        loading: false
      });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  initVoiceSession: async () => {
    set({ loading: true, error: null, interview_type: 'voice', voice_evaluations: [] });
    try {
      const response = await fetch(`${API_URL}/api/interview/voice/init`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          difficulty: get().difficulty,
          topic: get().topic,
          style: get().style
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to initialize Voice session.');
      }
      
      const data = await response.json();
      set({
        session_id: data.session_id,
        voice_question: data.question_text,
        voice_audio: data.audio_base64,
        current_view: 'voice',
        loading: false
      });
      
      // Auto-connect real-time WebSocket
      get().connectVoiceWebSocket();
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  connectVoiceWebSocket: () => {
    const sessionId = get().session_id;
    if (!sessionId) return;
    
    // Close existing if any
    const existingWs = get().websocket;
    if (existingWs) {
      existingWs.close();
    }
    
    const ws = new WebSocket(`${WS_URL}/api/websocket/voice/${sessionId}`);
    
    ws.onopen = () => {
      console.log('Voice interview WebSocket established.');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WS Event received:', data.event);
      
      if (data.event === 'processing_started') {
        set({ loading: true });
      } else if (data.event === 'evaluation_result') {
        const evalResult: VoiceEvaluation = data.evaluation;
        const nextQ = data.next_question;
        
        set((state) => ({
          voice_evaluations: [...state.voice_evaluations, evalResult],
          voice_question: nextQ.question_text,
          voice_audio: nextQ.audio_base64,
          transcription: '',
          loading: false
        }));
      } else if (data.event === 'error') {
        set({ error: data.message, loading: false });
      }
    };
    
    ws.onclose = () => {
      console.log('Voice interview WebSocket closed.');
    };
    
    ws.onerror = (err) => {
      console.error('WebSocket Error:', err);
      set({ error: 'WebSocket connection encountered an error.' });
    };
    
    set({ websocket: ws });
  },

  submitVoiceAnswer: (transcript) => {
    const ws = get().websocket;
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      set({ error: 'Connection is closed. Please refresh and retry.' });
      return;
    }
    
    set({ loading: true });
    ws.send(JSON.stringify({
      event: 'submit_answer',
      transcribed_text: transcript
    }));
  },

  finishVoiceSession: async () => {
    const sessionId = get().session_id;
    if (!sessionId) return;
    
    // Close websocket first
    const ws = get().websocket;
    if (ws) {
      ws.close();
    }
    
    set({ loading: true });
    try {
      const response = await fetch(`${API_URL}/api/interview/voice/summary/${sessionId}`);
      if (!response.ok) {
        throw new Error('Failed to load Voice session summary.');
      }
      const data = await response.json();
      set({
        voice_summary: data,
        current_view: 'summary',
        loading: false
      });
    } catch (err: any) {
      set({ error: err.message, loading: false });
    }
  },

  resetSession: () => {
    const ws = get().websocket;
    if (ws) {
      ws.close();
    }
    set({
      session_id: null,
      interview_type: null,
      current_view: 'dashboard',
      mcq_questions: [],
      current_mcq_index: 0,
      mcq_answers: {},
      mcq_summary: null,
      voice_question: null,
      voice_audio: null,
      voice_evaluations: [],
      voice_summary: null,
      transcription: '',
      is_recording: false,
      websocket: null,
      loading: false,
      error: null
    });
  }
}));
