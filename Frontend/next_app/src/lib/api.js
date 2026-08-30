/**
 * Vibhu-Oska API Client
 * Centralized backend configuration and fetch helpers.
 * All endpoints point to the FastAPI gateway on port 8100.
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8100';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://127.0.0.1:8100/ws';

export const API = {
  BASE: BACKEND_URL,
  WS: WS_URL,

  endpoints: {
    health: '/health',
    status: '/status',
    telemetry: '/api/v1/telemetry',
    chat: '/api/v1/chat',
    search: '/api/v1/search',
    memoryQuery: '/api/v1/memory/query',
    memoryStore: '/api/v1/memory/store',
    memoryKG: '/api/v1/memory/kg',
    sessions: '/api/v1/sessions',
    corpusAppend: '/api/v1/corpus/append',
    modelTrain: '/api/v1/model/train',
    trainingStatus: '/api/v1/training/status',
    schedulerTasks: '/api/v1/scheduler/tasks',
    selfUpdate: '/api/v1/self-update',
    plugins: '/api/v1/plugins',
    events: '/api/v1/events',
  },

  wsEvents: {
    ACK: 'ack',
    TASK_CREATED: 'task.created',
    TASK_COMPLETED: 'task.completed',
    TASK_FAILED: 'task.failed',
    TRAINING_LOG: 'system.model_training_log',
  },
};

export function buildUrl(endpoint) {
  return `${BACKEND_URL}${endpoint}`;
}

export function buildWsUrl() {
  return WS_URL;
}

export async function apiFetch(endpoint, options = {}) {
  const url = buildUrl(endpoint);
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`;
    try {
      const errData = await response.json();
      errorMessage = errData.detail || errData.message || errorMessage;
    } catch {
      // ignore parse error
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

export async function apiPost(endpoint, body) {
  return apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function apiGet(endpoint) {
  return apiFetch(endpoint, { method: 'GET' });
}

export function createWebSocket() {
  return new WebSocket(WS_URL);
}