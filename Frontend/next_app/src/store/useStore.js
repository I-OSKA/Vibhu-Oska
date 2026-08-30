import { create } from 'zustand';

export const useStore = create((set, get) => ({
  // Navigation
  activePage: 'dashboard', // dashboard | config | playground | research | code | sandbox | admin | docs | training
  setActivePage: (page) => set({ activePage: page }),

  // Telemetry (Real-time hardware data fetched from backend)
  telemetry: {
    gpuUtil: 0,
    cpuUtil: 0,
    ramUtil: 0,
    gpuTemp: 0,
    gpuPower: 0,
    uptime: '0h 0m 0s'
  },
  setTelemetry: (telemetry) => set({ telemetry }),

  // Real-time Training State (driven by WS events + API status)
  trainingActive: false,
  trainingLogs: [],
  trainingStartedAt: null,
  appendTrainingLog: (log) => set((state) => ({
    trainingLogs: [...state.trainingLogs, log].slice(-100)
  })),
  setTrainingStatus: (active) => set((state) => ({
    trainingActive: active,
    trainingStartedAt: active ? new Date().toISOString() : state.trainingStartedAt
  })),
  clearTrainingLogs: () => set({ trainingLogs: [] }),

  // Local Chat / Playground (ChatGPT/Gemini style)
  chatHistory: [
    { role: 'assistant', content: 'Vibhu-Oska AI-OS ready. All operations are strictly local. No API connections enabled.', thinking: 'System initialized locally on CPU/GPU framework.' }
  ],
  addChatMessage: (msg) => set((state) => ({
    chatHistory: [...state.chatHistory, msg]
  })),
  clearChatHistory: () => set({
    chatHistory: [
      { role: 'assistant', content: 'Vibhu-Oska AI-OS ready. All operations are strictly local. No API connections enabled.', thinking: 'System initialized locally on CPU/GPU framework.' }
    ]
  }),

  // Local Knowledge Graph & Citations (Perplexity style)
  searchQuery: '',
  searchResults: null,
  setSearch: (query, results) => set({ searchQuery: query, searchResults: results }),

  // Local Code Workspace (Claude Code style)
  codeFiles: [
    { name: 'app.py', status: 'healthy', size: '22KB' },
    { name: 'cognition.py', status: 'healthy', size: '5.8KB' },
    { name: 'backup1.py', status: 'healed', size: '3.1KB' }
  ],
  codeLogs: ['Ready for autonomous AST diagnostics.'],
  addCodeLog: (log) => set((state) => ({ codeLogs: [log, ...state.codeLogs] })),

  // Odyssey Sandbox (Agent world grid coordinates)
  agents: [
    { id: 'Agent-Alpha', x: 2, y: 3, state: 'Searching Memory', log: 'Querying vector paths' },
    { id: 'Agent-Beta', x: 7, y: 5, state: 'Analyzing Code', log: 'Parsing AST for apps' },
    { id: 'Agent-Gamma', x: 4, y: 8, state: 'Training Router', log: 'Optimizing weight gradients' }
  ],
  updateAgentPositions: () => set((state) => ({
    agents: state.agents.map(a => {
      const dx = Math.floor(Math.random() * 3) - 1;
      const dy = Math.floor(Math.random() * 3) - 1;
      const newX = Math.max(0, Math.min(10, a.x + dx));
      const newY = Math.max(0, Math.min(10, a.y + dy));
      return { ...a, x: newX, y: newY };
    })
  })),

  // Self-Updater
  updaterStatus: 'idle', // idle | testing | patching | verification
  updaterLogs: ['Self-healing system ready.'],
  setUpdater: (status, logs) => set({ updaterStatus: status, updaterLogs: logs }),
  addUpdaterLog: (log) => set((state) => ({ updaterLogs: [log, ...state.updaterLogs] }))
}));