const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('terminalAPI', {
  getConfig: () => ipcRenderer.invoke('get-config'),
  spawnPty: (id, command, args, cols, rows) =>
    ipcRenderer.invoke('spawn-pty', { id, command, args, cols, rows }),
  write: (id, data) => ipcRenderer.send('pty-write', { id, data }),
  resize: (id, cols, rows) => ipcRenderer.send('pty-resize', { id, cols, rows }),
  kill: (id) => ipcRenderer.send('pty-kill', { id }),
  onData: (id, callback) => {
    const channel = `pty-data-${id}`;
    ipcRenderer.removeAllListeners(channel);
    ipcRenderer.on(channel, (_event, data) => callback(data));
  },
  onExit: (id, callback) => {
    const channel = `pty-exit-${id}`;
    ipcRenderer.removeAllListeners(channel);
    ipcRenderer.on(channel, (_event, exitCode) => callback(exitCode));
  }
});
