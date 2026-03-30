const { app } = require('electron');
app.whenReady().then(() => {
  try {
    const pty = require('node-pty');
    const proc = pty.spawn('cmd.exe', [], { cols: 80, rows: 24 });
    proc.onData(d => {
      console.log('PTY DATA:', d.substring(0, 80));
      proc.kill();
      app.quit();
    });
    setTimeout(() => { proc.kill(); app.quit(); }, 3000);
  } catch (err) {
    console.error('PTY LOAD ERROR:', err.message);
    app.quit();
  }
});
