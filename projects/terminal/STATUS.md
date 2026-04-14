# terminal — Status

**Last touched:** 2026-03-20  
**State:** Built, untested end-to-end

## What it is

Electron app: multi-pane terminal using xterm.js + node-pty.
Configurable panes via `panes.json`. Default: 2 horizontal panes running Git Bash.

## What was built

- `main.js` — Electron main process, IPC handlers, PTY manager integration
- `lib/pty-manager.js` — node-pty wrapper (spawn/kill/resize/write)
- `renderer.js` — xterm.js frontend, IPC bridge
- `preload.js` — context bridge (secure IPC)
- `index.html` + `styles.css` — layout
- `panes.json` — layout config (horizontal, 2 panes: Terminal + Helper)
- `start.bat` — launch script

## Current state

Built but **not verified working** since March 20. node-pty requires native compilation (`electron-rebuild`) — this may need to be re-run if Electron version changed.

## Known issues / risks

- `node-pty` native module — requires rebuild after `npm install` on this machine
- Electron 35 + node-pty 1.0 compatibility untested on current Node version
- DevTools open by default in `main.js` line 26 — should be removed before any real use

## Next step

1. `cd projects/terminal && npm install && npm run rebuild`
2. `npm start` — verify both panes open and accept input
3. Remove `win.webContents.openDevTools()` line once confirmed working
4. Consider: is this still needed given Claude-in-Chrome MCP and Windows Terminal?
