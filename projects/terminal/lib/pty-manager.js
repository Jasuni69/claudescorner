const pty = require('node-pty');
const os = require('os');

class PtyManager {
  constructor() {
    this.ptys = new Map();
  }

  spawn(id, command, args = [], cols = 80, rows = 24) {
    if (this.ptys.has(id)) this.kill(id);

    const shell = command || (os.platform() === 'win32' ? 'bash.exe' : 'bash');
    const env = Object.assign({}, process.env);
    // Clear Claude Code env vars to avoid nested session conflicts
    delete env.CLAUDECODE;
    delete env.CLAUDE_CODE;
    delete env.CLAUDE_CODE_ENTRYPOINT;

    const proc = pty.spawn(shell, args, {
      name: 'xterm-256color',
      cols,
      rows,
      cwd: os.homedir(),
      env
    });

    this.ptys.set(id, proc);
    return proc;
  }

  has(id) {
    return this.ptys.has(id);
  }

  write(id, data) {
    const proc = this.ptys.get(id);
    if (proc) proc.write(data);
  }

  resize(id, cols, rows) {
    const proc = this.ptys.get(id);
    if (proc) proc.resize(cols, rows);
  }

  kill(id) {
    const proc = this.ptys.get(id);
    if (proc) {
      proc.kill();
      this.ptys.delete(id);
    }
  }

  killAll() {
    for (const id of this.ptys.keys()) this.kill(id);
  }

  onData(id, callback) {
    const proc = this.ptys.get(id);
    if (proc) proc.onData(callback);
  }

  onExit(id, callback) {
    const proc = this.ptys.get(id);
    if (proc) proc.onExit(callback);
  }
}

module.exports = PtyManager;
