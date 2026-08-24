/**
 * ==================================================
 * REETA — ui/electron/main.js
 * ==================================================
 * PURPOSE:
 *   The Electron main process. Creates the native window,
 *   manages lifecycle, and handles IPC from the renderer.
 *
 * PHASE 4.5 HARDENING:
 *   - contextIsolation: true (prevents XSS from accessing Node)
 *   - nodeIntegration: false (renderer cannot require('fs') etc.)
 *   - preload.js bridge for safe IPC
 *   - Crash recovery: auto-restarts the renderer on crash
 *   - Graceful shutdown: cleans up resources before quitting
 * ==================================================
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const os = require('os');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      // SECURITY: Do NOT allow Node.js in the renderer
      nodeIntegration: false,
      // SECURITY: Isolate renderer context from preload
      contextIsolation: true,
      // SECURITY: Use a preload script for safe IPC
      preload: path.join(__dirname, 'preload.cjs'),
      // Performance: enable hardware acceleration
      backgroundThrottling: false,
    },
    autoHideMenuBar: true,
    // Native-looking dark title bar on Windows
    backgroundColor: '#030712',
    show: false, // Don't show until ready to prevent white flash
  });

  const isDev = process.env.NODE_ENV !== 'production';

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Show window only after content is painted (no white flash)
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // --- Crash Recovery ---
  // If the renderer process crashes, automatically reload it
  mainWindow.webContents.on('render-process-gone', (_event, details) => {
    console.error(`[REETA Electron] Renderer crashed: ${details.reason}`);
    if (details.reason !== 'clean-exit') {
      console.log('[REETA Electron] Attempting to reload renderer...');
      setTimeout(() => {
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.reload();
        }
      }, 2000);
    }
  });

  // Catch unresponsive renderer
  mainWindow.on('unresponsive', () => {
    console.warn('[REETA Electron] Window became unresponsive. Reloading...');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.reload();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// --- IPC Handlers ---
ipcMain.handle('get-app-version', () => app.getVersion());

ipcMain.handle('get-platform-info', () => ({
  platform: process.platform,
  arch: process.arch,
  nodeVersion: process.versions.node,
  electronVersion: process.versions.electron,
  totalMemoryGB: (os.totalmem() / (1024 ** 3)).toFixed(1),
  freeMemoryGB: (os.freemem() / (1024 ** 3)).toFixed(1),
  cpuCores: os.cpus().length,
}));

ipcMain.on('quit-app', () => {
  app.quit();
});

ipcMain.on('minimize-window', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on('maximize-window', () => {
  if (mainWindow) {
    mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize();
  }
});

ipcMain.on('close-window', () => {
  if (mainWindow) mainWindow.close();
});

// --- App Lifecycle ---
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Catch unhandled exceptions in the main process
process.on('uncaughtException', (error) => {
  console.error('[REETA Electron] Uncaught Main Process Exception:', error);
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('main-process-error', error.message);
  }
});
