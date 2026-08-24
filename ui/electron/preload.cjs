/**
 * ==================================================
 * REETA — ui/electron/preload.js
 * ==================================================
 * PURPOSE:
 *   Secure IPC bridge between Electron's main process and
 *   the React renderer. This is the ONLY way the frontend
 *   should communicate with Node.js APIs.
 *
 *   With contextIsolation: true, the React app cannot
 *   access Node.js directly. Instead, it calls methods
 *   exposed here via window.electronAPI.
 * ==================================================
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // App lifecycle
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  quitApp: () => ipcRenderer.send('quit-app'),

  // Window controls (for a custom titlebar later)
  minimizeWindow: () => ipcRenderer.send('minimize-window'),
  maximizeWindow: () => ipcRenderer.send('maximize-window'),
  closeWindow: () => ipcRenderer.send('close-window'),

  // Diagnostics: receive crash/error info from the main process
  onMainProcessError: (callback) => {
    ipcRenderer.on('main-process-error', (_event, message) => callback(message));
  },

  // Platform info
  getPlatformInfo: () => ipcRenderer.invoke('get-platform-info'),
});
