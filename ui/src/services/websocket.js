/**
 * ==================================================
 * REETA — ui/src/services/websocket.js
 * ==================================================
 * PURPOSE:
 *   Manages the WebSocket connection between the React UI
 *   and the FastAPI backend.
 *
 * PHASE 4.5 HARDENING:
 *   - Heartbeat ping/pong to detect zombie connections
 *   - Exponential backoff on reconnects (caps at 30s)
 *   - LOG_EVENT batching to prevent React re-render flooding
 *   - Clean disconnect and resource cleanup
 * ==================================================
 */

import useStore from '../store/useStore';

// How often (ms) to send a heartbeat ping
const HEARTBEAT_INTERVAL_MS = 15000;
// How long (ms) to wait for a pong reply before considering the connection dead
const HEARTBEAT_TIMEOUT_MS = 10000;
// How often (ms) to flush batched log events to the store
const LOG_BATCH_FLUSH_MS = 300;

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectTimer = null;
    this.heartbeatInterval = null;
    this.heartbeatTimeout = null;
    this.reconnectAttempts = 0;

    // Log batching: accumulate rapid LOG_EVENT messages
    // and flush them to Zustand in a single batch
    this._logBatch = [];
    this._logFlushTimer = null;
  }

  connect() {
    // Prevent duplicate connections
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    try {
      this.ws = new WebSocket('ws://127.0.0.1:8000/ws');
    } catch (e) {
      console.error('[REETA WS] Failed to create WebSocket:', e);
      this._scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      console.log('[REETA WS] Connected to backend');
      useStore.getState().setWsConnected(true);
      this.reconnectAttempts = 0; // Reset backoff on successful connection
      this._startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle heartbeat pong from the backend
        if (data.type === 'PONG') {
          this._onHeartbeatPong();
          return;
        }

        this.handleEvent(data.type, data.payload);
      } catch (e) {
        console.error('[REETA WS] Failed to parse message:', e);
      }
    };

    this.ws.onclose = (event) => {
      console.log(`[REETA WS] Disconnected (code: ${event.code})`);
      useStore.getState().setWsConnected(false);
      this._stopHeartbeat();
      this._flushLogBatch(); // Flush any remaining logs
      this._scheduleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('[REETA WS] Error:', error);
      // Don't call ws.close() here — the onclose handler will fire automatically
    };
  }

  disconnect() {
    // Clean shutdown
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this._stopHeartbeat();
    this._flushLogBatch();
    if (this.ws) {
      this.ws.onclose = null; // Prevent reconnect on intentional disconnect
      this.ws.close();
      this.ws = null;
    }
    useStore.getState().setWsConnected(false);
  }

  // --- Heartbeat System ---
  _startHeartbeat() {
    this._stopHeartbeat(); // Clear any existing timers
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        // Send a PING to the backend
        this.ws.send(JSON.stringify({ type: 'PING' }));

        // Start a timeout — if no PONG comes back, the connection is dead
        this.heartbeatTimeout = setTimeout(() => {
          console.warn('[REETA WS] Heartbeat timeout — connection is stale. Reconnecting...');
          if (this.ws) this.ws.close();
        }, HEARTBEAT_TIMEOUT_MS);
      }
    }, HEARTBEAT_INTERVAL_MS);
  }

  _onHeartbeatPong() {
    // Backend replied to our ping — connection is alive
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  _stopHeartbeat() {
    if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
    if (this.heartbeatTimeout) clearTimeout(this.heartbeatTimeout);
    this.heartbeatInterval = null;
    this.heartbeatTimeout = null;
  }

  // --- Reconnection with Exponential Backoff ---
  _scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    // Exponential backoff: 1s, 2s, 4s, 8s, ... up to 30s
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectAttempts++;
    console.log(`[REETA WS] Reconnecting in ${delay / 1000}s (attempt ${this.reconnectAttempts})...`);
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }

  // --- Log Event Batching ---
  // Instead of calling addLog() on every single LOG_EVENT (which triggers
  // a React re-render each time), we accumulate logs in a buffer and
  // flush them to the store in a single batch every LOG_BATCH_FLUSH_MS.
  _queueLog(logEntry) {
    this._logBatch.push(logEntry);
    if (!this._logFlushTimer) {
      this._logFlushTimer = setTimeout(() => this._flushLogBatch(), LOG_BATCH_FLUSH_MS);
    }
  }

  _flushLogBatch() {
    if (this._logFlushTimer) {
      clearTimeout(this._logFlushTimer);
      this._logFlushTimer = null;
    }
    if (this._logBatch.length > 0) {
      useStore.getState().addLogBatch(this._logBatch);
      this._logBatch = [];
    }
  }

  // --- Event Router ---
  handleEvent(type, payload) {
    const store = useStore.getState();
    switch (type) {
      case 'VOICE_STATE':
        store.setVoiceState(payload.state);
        break;
      case 'CHAT_MESSAGE':
        store.addMessage({ role: payload.role, content: payload.content });
        break;
      case 'LOG_EVENT':
        // Batched instead of immediate to prevent render flooding
        this._queueLog(payload);
        break;
      case 'WORKFLOW_START':
        store.setActiveWorkflow(payload.workflow);
        store.setWorkflowSteps(payload.steps || []);
        break;
      case 'WORKFLOW_END':
        store.setActiveWorkflow(null);
        break;
      default:
        console.warn('[REETA WS] Unknown event type:', type);
    }
  }

  sendMessage(text) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'CHAT_MESSAGE', content: text }));
      useStore.getState().addMessage({ role: 'user', content: text });
      useStore.getState().setVoiceState('processing');
    } else {
      console.warn('[REETA WS] Cannot send — socket not open');
    }
  }
}

export const wsService = new WebSocketService();
