/**
 * ==================================================
 * REETA — ui/src/store/useStore.js
 * ==================================================
 * PURPOSE:
 *   Global state management via Zustand.
 *
 * PHASE 4.5 HARDENING:
 *   - Strict max limits on messages and logs to prevent
 *     memory leaks during long-running sessions.
 *   - addLogBatch() for batched log insertion (used by the
 *     WebSocket service to prevent render flooding).
 *   - clearLogs() and clearMessages() for diagnostics.
 * ==================================================
 */

import { create } from 'zustand';

const MAX_MESSAGES = 500;
const MAX_LOGS = 500;

const useStore = create((set) => ({
  // --- WebSocket State ---
  wsConnected: false,
  setWsConnected: (status) => set({ wsConnected: status }),

  // --- Voice State (idle, listening, processing, speaking) ---
  voiceState: 'idle',
  setVoiceState: (state) => set({ voiceState: state }),

  // --- Chat State ---
  messages: [
    { role: 'assistant', content: 'Hello! I am REETA. How can I assist you today?' }
  ],
  addMessage: (message) => set((state) => ({
    // Enforce max message count to prevent memory growth
    messages: [...state.messages, message].slice(-MAX_MESSAGES)
  })),
  clearMessages: () => set({
    messages: [{ role: 'assistant', content: 'Chat cleared. How can I help?' }]
  }),

  // --- Automation State ---
  activeWorkflow: null,
  setActiveWorkflow: (workflow) => set({ activeWorkflow: workflow }),
  workflowSteps: [],
  setWorkflowSteps: (steps) => set({ workflowSteps: steps }),

  // --- Memory State ---
  memories: [],
  setMemories: (memories) => set({ memories }),

  // --- Logs State ---
  logs: [],
  // Single log insert (still available for non-batched use)
  addLog: (log) => set((state) => ({
    logs: [...state.logs, log].slice(-MAX_LOGS)
  })),
  // Batch log insert — used by the WebSocket service
  // to flush multiple logs in a single React render cycle
  addLogBatch: (batch) => set((state) => ({
    logs: [...state.logs, ...batch].slice(-MAX_LOGS)
  })),
  clearLogs: () => set({ logs: [] }),
}));

export default useStore;
