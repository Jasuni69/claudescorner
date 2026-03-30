const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const PtyManager = require('./lib/pty-manager');

const ptyManager = new PtyManager();

function loadConfig() {
  const configPath = path.join(__dirname, 'panes.json');
  return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 800,
    backgroundColor: '#1a1a2e',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadFile('index.html');
  win.webContents.openDevTools({ mode: 'detach' });
  win.on('closed', () => ptyManager.killAll());
}

// IPC handlers
ipcMain.handle('get-config', () => loadConfig());

ipcMain.handle('spawn-pty', (_event, { id, command, args, cols, rows }) => {
  // Kill existing if respawning
  if (ptyManager.has(id)) ptyManager.kill(id);

  let proc;
  try {
    proc = ptyManager.spawn(id, command, args, cols, rows);
  } catch (err) {
    console.error(`spawn-pty error for ${id}:`, err.message);
    return { error: err.message };
  }
  const win = BrowserWindow.getAllWindows()[0];

  ptyManager.onData(id, (data) => {
    if (win && !win.isDestroyed()) {
      win.webContents.send(`pty-data-${id}`, data);
    }
  });

  ptyManager.onExit(id, (exitCode) => {
    if (win && !win.isDestroyed()) {
      win.webContents.send(`pty-exit-${id}`, exitCode);
    }
  });

  return { pid: proc.pid };
});

ipcMain.on('pty-write', (_event, { id, data }) => ptyManager.write(id, data));
ipcMain.on('pty-resize', (_event, { id, cols, rows }) => ptyManager.resize(id, cols, rows));
ipcMain.on('pty-kill', (_event, { id }) => ptyManager.kill(id));

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  ptyManager.killAll();
  app.quit();
});
