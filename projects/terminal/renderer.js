/* globals loaded via script tags */
const { Terminal } = window;
const { FitAddon } = window.FitAddon;

const panes = new Map(); // id → { term, fitAddon, paneEl, config }
let activePaneId = null;
let paneCounter = 0;

async function init() {
  const config = await window.terminalAPI.getConfig();
  for (const pane of config.panes) {
    await createPane(pane);
  }
  // Focus first pane
  if (config.panes.length > 0) setActivePane(config.panes[0].id);
  setupKeybindings();
}

async function createPane(paneConfig) {
  const container = document.getElementById('pane-container');
  const id = paneConfig.id || `pane-${++paneCounter}`;
  paneConfig.id = id;

  // DOM
  const paneEl = document.createElement('div');
  paneEl.className = 'pane';
  paneEl.style.flex = paneConfig.flex || 1;
  paneEl.dataset.paneId = id;

  const header = document.createElement('div');
  header.className = 'pane-header';

  const titleSpan = document.createElement('span');
  titleSpan.className = 'pane-title';
  titleSpan.textContent = paneConfig.title || id;

  const controls = document.createElement('div');
  controls.className = 'pane-controls';

  const restartBtn = document.createElement('button');
  restartBtn.className = 'pane-btn restart-btn';
  restartBtn.textContent = '↻';
  restartBtn.title = 'Restart';
  restartBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    restartPane(id);
  });

  const closeBtn = document.createElement('button');
  closeBtn.className = 'pane-btn close-btn';
  closeBtn.textContent = '✕';
  closeBtn.title = 'Close';
  closeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    removePane(id);
  });

  controls.appendChild(restartBtn);
  controls.appendChild(closeBtn);
  header.appendChild(titleSpan);
  header.appendChild(controls);

  const body = document.createElement('div');
  body.className = 'pane-body';

  paneEl.appendChild(header);
  paneEl.appendChild(body);
  container.appendChild(paneEl);

  // Click to focus
  paneEl.addEventListener('mousedown', () => setActivePane(id));

  // Terminal
  const term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
    fontFamily: "'Consolas', 'Courier New', monospace",
    theme: {
      background: '#0f0f1a',
      foreground: '#e0e0e0',
      cursor: '#e0e0e0',
      selectionBackground: '#3a3a5c'
    }
  });

  const fitAddon = new FitAddon();
  term.loadAddon(fitAddon);
  term.open(body);

  const entry = { term, fitAddon, paneEl, config: paneConfig, alive: false };
  panes.set(id, entry);

  // Fit + spawn
  requestAnimationFrame(() => {
    fitAddon.fit();
    spawnProcess(id);
  });

  // Resize observer
  const ro = new ResizeObserver(() => {
    fitAddon.fit();
    if (entry.alive) {
      window.terminalAPI.resize(id, term.cols, term.rows);
    }
  });
  ro.observe(body);

  return id;
}

async function spawnProcess(id) {
  const entry = panes.get(id);
  if (!entry) return;
  const { term, config } = entry;

  console.log(`Spawning ${id}: ${config.command} ${(config.args||[]).join(' ')}`);
  const result = await window.terminalAPI.spawnPty(
    id, config.command, config.args || [], term.cols, term.rows
  );
  console.log(`Spawn result for ${id}:`, result);
  if (result && result.error) {
    term.write(`\r\n\x1b[31m[Spawn error: ${result.error}]\x1b[0m\r\n`);
    return;
  }
  entry.alive = true;

  window.terminalAPI.onData(id, (data) => {
    console.log(`[${id}] got data:`, data.substring(0, 40));
    term.write(data);
  });
  term.onData((data) => {
    console.log(`[${id}] sending:`, JSON.stringify(data));
    window.terminalAPI.write(id, data);
  });

  window.terminalAPI.onExit(id, (code) => {
    entry.alive = false;
    term.write(`\r\n\x1b[90m[exited ${code}]\x1b[0m\r\n`);
    entry.paneEl.classList.add('exited');
  });
}

function restartPane(id) {
  const entry = panes.get(id);
  if (!entry) return;

  if (entry.alive) {
    window.terminalAPI.kill(id);
  }
  entry.term.clear();
  entry.paneEl.classList.remove('exited');

  // Small delay to let old process die
  setTimeout(() => spawnProcess(id), 100);
}

function removePane(id) {
  const entry = panes.get(id);
  if (!entry) return;

  if (entry.alive) window.terminalAPI.kill(id);
  entry.term.dispose();
  entry.paneEl.remove();
  panes.delete(id);

  // Focus neighbor
  if (activePaneId === id) {
    const ids = [...panes.keys()];
    if (ids.length > 0) setActivePane(ids[ids.length - 1]);
    else activePaneId = null;
  }
}

function setActivePane(id) {
  if (!panes.has(id)) return;
  // Remove active from old
  if (activePaneId && panes.has(activePaneId)) {
    panes.get(activePaneId).paneEl.classList.remove('active');
  }
  activePaneId = id;
  const entry = panes.get(id);
  entry.paneEl.classList.add('active');
  entry.term.focus();
}

function cyclePane(direction = 1) {
  const ids = [...panes.keys()];
  if (ids.length <= 1) return;
  const idx = ids.indexOf(activePaneId);
  const next = (idx + direction + ids.length) % ids.length;
  setActivePane(ids[next]);
}

async function addNewPane() {
  paneCounter++;
  const id = `shell-${paneCounter}`;
  await createPane({
    id,
    title: `Shell ${paneCounter}`,
    command: 'C:\\Program Files\\Git\\bin\\bash.exe',
    args: [],
    flex: 1
  });
  setActivePane(id);
}

function setupKeybindings() {
  document.addEventListener('keydown', (e) => {
    // Ctrl+Shift+T — new pane
    if (e.ctrlKey && e.shiftKey && e.key === 'T') {
      e.preventDefault();
      addNewPane();
      return;
    }
    // Ctrl+W — close active pane
    if (e.ctrlKey && !e.shiftKey && e.key === 'w') {
      e.preventDefault();
      if (activePaneId && panes.size > 1) removePane(activePaneId);
      return;
    }
    // Ctrl+Tab / Ctrl+Shift+Tab — cycle panes
    if (e.ctrlKey && e.key === 'Tab') {
      e.preventDefault();
      cyclePane(e.shiftKey ? -1 : 1);
      return;
    }
    // Ctrl+Shift+R — restart active pane
    if (e.ctrlKey && e.shiftKey && e.key === 'R') {
      e.preventDefault();
      if (activePaneId) restartPane(activePaneId);
      return;
    }
  });
}

init();
