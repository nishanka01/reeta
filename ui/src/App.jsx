/**
 * ==================================================
 * REETA — ui/src/App.jsx
 * ==================================================
 * PURPOSE:
 *   Futuristic Stitch HUD Intelligence System Interface.
 *   Assembles all navigation tabs (Home, Neural Link, World,
 *   Automation, Profile) into a unified react component shell.
 * ==================================================
 */

import React, { useState, useEffect, useRef } from 'react';
import { wsService } from './services/websocket';
import useStore from './store/useStore';

function App() {
  const wsConnected = useStore((state) => state.wsConnected);
  const [activePage, setActivePage] = useState('home');
  const [clockStr, setClockStr] = useState('');
  const [cpuUsage, setCpuUsage] = useState(34);
  const [logs, setLogs] = useState([
    { id: 1, time: '12:00:01', msg: 'REETA OS INITIALIZED', type: 'info' },
    { id: 2, time: '12:02:45', msg: 'Neural link established with Node-04', type: 'info' },
    { id: 3, time: '12:04:02', msg: 'Opened Chrome application', type: 'info' },
    { id: 4, time: '12:05:12', msg: 'Search query: "Advanced Automation Logic"', type: 'accent' },
    { id: 5, time: '12:08:19', msg: 'Buffer stream stabilized at 4.2Gbps', type: 'info' }
  ]);
  const [cmdInput, setCmdInput] = useState('');
  const terminalRef = useRef(null);

  useEffect(() => {
    wsService.connect();
    return () => wsService.disconnect();
  }, []);

  // Live clock
  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setClockStr(now.toLocaleTimeString('en-GB', { hour12: false }) + ' IST');
    }, 1000);
    setClockStr(new Date().toLocaleTimeString('en-GB', { hour12: false }) + ' IST');
    return () => clearInterval(timer);
  }, []);

  // CPU Usage fluctuation simulation
  useEffect(() => {
    const timer = setInterval(() => {
      setCpuUsage(Math.floor(28 + Math.random() * 20));
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  // Auto-scroll terminal log
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const addLog = (msg, type = 'info') => {
    const time = new Date().toLocaleTimeString('en-GB', { hour12: false });
    setLogs((prev) => [...prev.slice(-19), { id: Date.now() + Math.random(), time, msg, type }]);
  };

  const handleHexClick = (action) => {
    addLog(`MANUAL OVERRIDE: ${action}`, 'override');
  };

  const handleCmdSubmit = (e) => {
    if (e.key === 'Enter' && cmdInput.trim()) {
      addLog(`$ ${cmdInput.trim()}`, 'cmd');
      setCmdInput('');
    }
  };

  return (
    <div className="hud-grid text-on-surface font-body-md w-screen h-screen overflow-hidden relative">
      {/* Global Scanline */}
      <div className="scanline" />

      {/* ======================== SIDEBAR NAV ======================== */}
      <nav id="sidebar" className="fixed left-4 top-4 bottom-4 w-64 rounded-xl border border-primary/20 bg-surface/5 backdrop-blur-md shadow-[0_0_20px_rgba(0,219,231,0.1)] flex flex-col py-6 px-4 z-50">
        <div className="mb-10 flex flex-col items-center gap-1">
          <div className="font-display-lg text-display-lg text-primary drop-shadow-[0_0_12px_rgba(0,219,231,0.6)] leading-none tracking-tight">
            REETA AI
          </div>
          <div className="font-label-caps text-label-caps text-primary/60 tracking-widest">
            V-4.2 STATUS: ACTIVE
          </div>
        </div>

        <div className="flex-1 space-y-1.5">
          {[
            { id: 'home', label: 'Home', icon: 'home' },
            { id: 'chat', label: 'Neural Link', icon: 'graphic_eq' },
            { id: 'world', label: 'World', icon: 'public' },
            { id: 'automation', label: 'Automation', icon: 'settings_suggest' },
            { id: 'profile', label: 'Profile', icon: 'account_circle' }
          ].map((item) => {
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`flex items-center gap-4 w-full px-4 py-3 rounded-lg font-label-caps text-label-caps transition-all duration-300 ${
                  isActive
                    ? 'text-primary border-r-2 border-primary bg-primary/10'
                    : 'text-on-surface-variant/70 hover:text-primary/80 hover:bg-primary/5'
                }`}
              >
                <span
                  className="material-symbols-outlined"
                  style={{ fontVariationSettings: isActive ? "'FILL' 1" : "'FILL' 0" }}
                >
                  {item.icon}
                </span>
                {item.label}
              </button>
            );
          })}
        </div>

        <button
          onClick={() => setActivePage('chat')}
          className="mt-auto w-full py-4 border border-primary/40 rounded-lg font-label-caps text-label-caps text-primary hover:bg-primary/10 hover:border-primary transition-all active:scale-95 group cursor-pointer"
        >
          <span className="group-hover:drop-shadow-[0_0_8px_#00dbe7]">INITIALIZE NEURAL LINK</span>
        </button>
      </nav>

      {/* ======================== TOP BAR ======================== */}
      <header className="fixed top-0 right-0 left-72 h-16 border-b border-primary/10 flex justify-between items-center px-8 z-40 bg-surface-container-lowest/60 backdrop-blur-lg">
        <div className="flex items-center gap-4">
          <span className="material-symbols-outlined text-primary animate-pulse">radar</span>
          <span className="font-data-mono text-data-mono text-primary uppercase tracking-[0.15em] flicker">
            ALL SYSTEMS NOMINAL — 3 REMINDERS ACTIVE
          </span>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex flex-col items-end">
            <span className="font-label-caps text-label-caps text-on-surface-variant">NODE_ID: 771-X</span>
            <span className={`font-data-mono text-[10px] ${wsConnected ? 'text-primary/70' : 'text-error'}`}>
              WEBSOCKET: {wsConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
          <div className="font-data-mono text-xs text-primary/60">{clockStr}</div>
          <button
            onClick={() => setActivePage('chat')}
            className="p-2 border border-primary/20 rounded-full hover:bg-primary/10 transition-all cursor-pointer"
            title="Neural Link"
          >
            <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
              record_voice_over
            </span>
          </button>
        </div>
      </header>

      {/* ======================== MAIN CONTENT AREA ======================== */}
      <main className="fixed top-16 right-0 left-72 bottom-0 overflow-hidden">
        {/* ===== VIEW: HOME (HUD Dashboard) ===== */}
        {activePage === 'home' && (
          <div className="view active flex-col h-full p-8 overflow-hidden">
            <div className="grid grid-cols-12 grid-rows-6 gap-5 h-full">
              {/* Weather Station */}
              <div className="col-span-3 row-span-3 relative bg-surface-container-lowest/40 backdrop-blur-md rounded-xl border border-primary/20 p-6 overflow-hidden group">
                <div className="corner-bracket cb-tl" />
                <div className="corner-bracket cb-br" />
                <div className="scanner-line absolute left-0 right-0 z-0 opacity-10" />
                <h3 class="font-label-caps text-label-caps text-primary mb-6 flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm">thermostat</span> WEATHER_STATION
                </h3>
                <div className="flex flex-col items-center justify-center py-2">
                  <div className="relative w-36 h-36">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle className="text-primary/10" cx="72" cy="72" fill="transparent" r="60" stroke="currentColor" strokeWidth="2" />
                      <circle className="text-primary drop-shadow-[0_0_5px_rgba(0,219,231,0.8)]" cx="72" cy="72" fill="transparent" r="60" stroke="currentColor" strokeDasharray="377" strokeDashoffset="94" strokeWidth="4" />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="font-display-lg text-[38px] leading-none text-primary text-glow">24°C</span>
                      <span className="font-label-caps text-[10px] text-on-surface-variant mt-1">HUMIDITY: 42%</span>
                    </div>
                  </div>
                  <div className="mt-5 w-full grid grid-cols-2 gap-3">
                    <div className="border-l border-primary/30 pl-2">
                      <div className="font-label-caps text-[10px] text-on-surface-variant">WIND</div>
                      <div className="font-data-mono text-primary">12 KM/H</div>
                    </div>
                    <div className="border-l border-primary/30 pl-2">
                      <div className="font-label-caps text-[10px] text-on-surface-variant">UV INDEX</div>
                      <div className="font-data-mono text-primary">MODERATE</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Voice Core (center) */}
              <div className="col-span-6 row-span-4 relative flex flex-col items-center justify-center cursor-pointer" onClick={() => setActivePage('chat')}>
                <div className="absolute inset-0 z-0 flex items-center justify-center">
                  <div className="w-80 h-80 rounded-full border border-primary/10 animate-pulse-ring" />
                  <div className="absolute w-[360px] h-[360px] rounded-full border border-primary/5 animate-pulse-ring" style={{ animationDelay: '1s' }} />
                  <div className="absolute w-[420px] h-[420px] rounded-full border border-primary/5 animate-pulse-ring" style={{ animationDelay: '2s' }} />
                </div>
                <div className="relative z-10 w-56 h-56 group">
                  <div className="absolute inset-0 rounded-full border-2 border-primary/40 group-hover:border-primary transition-all glow-cyan flex items-center justify-center">
                    <div className="text-center">
                      <span className="material-symbols-outlined text-primary text-5xl animate-pulse">mic</span>
                      <div className="font-label-caps text-label-caps text-primary mt-2">LISTENING</div>
                    </div>
                  </div>
                </div>
                <div className="mt-10 text-center relative z-10">
                  <div className="font-data-mono text-primary text-lg text-glow mb-1">
                    "Analyze morning briefing and plot navigation to Sector 7"
                  </div>
                  <div className="font-label-caps text-on-surface-variant text-[10px] tracking-widest opacity-50">
                    HEARING_INPUT_STREAM_ENCRYPTED
                  </div>
                </div>
              </div>

              {/* Reminders */}
              <div className="col-span-3 row-span-3 relative bg-surface-container-lowest/40 backdrop-blur-md rounded-xl border border-primary/20 p-6 overflow-hidden">
                <div className="corner-bracket cb-tl" />
                <div className="corner-bracket cb-br" />
                <h3 className="font-label-caps text-label-caps text-primary mb-6 flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm">alarm</span> TEMPORAL_LOGS
                </h3>
                <div className="space-y-5">
                  <div className="relative pl-4 border-l-2 border-primary/60">
                    <div className="font-label-caps text-label-caps text-primary">ORBITAL REVIEW</div>
                    <div className="font-data-mono text-on-surface-variant text-xs mb-1">T-MINUS 00:42:12</div>
                    <div className="w-full bg-primary/10 h-1 rounded-full overflow-hidden">
                      <div className="bg-primary h-full w-[65%]" />
                    </div>
                  </div>
                  <div className="relative pl-4 border-l-2 border-primary/20">
                    <div className="font-label-caps text-label-caps text-on-surface-variant">NEURAL MAINTENANCE</div>
                    <div className="font-data-mono text-on-surface-variant/50 text-xs">T-MINUS 04:15:00</div>
                  </div>
                  <div className="relative pl-4 border-l-2 border-primary/20">
                    <div className="font-label-caps text-label-caps text-on-surface-variant">SECTOR SYNC</div>
                    <div className="font-data-mono text-on-surface-variant/50 text-xs">T-MINUS 12:00:00</div>
                  </div>
                </div>
                <div className="mt-8 p-3 border border-secondary/30 bg-secondary/5 rounded-lg flex items-start gap-3">
                  <span className="material-symbols-outlined text-secondary text-sm mt-0.5">warning</span>
                  <div>
                    <div className="font-label-caps text-[10px] text-secondary">PRIORITY ALERT</div>
                    <p className="font-body-md text-xs text-on-surface leading-snug">Packet loss detected in subsystem grid. Recommended re-route.</p>
                  </div>
                </div>
              </div>

              {/* Market Ticker */}
              <div className="col-span-4 row-span-2 relative bg-surface-container-lowest/40 backdrop-blur-md rounded-xl border border-primary/20 p-5 overflow-hidden">
                <div className="corner-bracket cb-tl" />
                <h3 className="font-label-caps text-label-caps text-primary mb-4 flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm">monitoring</span> MARKET_TICKER
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="font-data-mono text-on-surface text-sm">NVDA_SYS</span>
                    <span className="font-data-mono text-primary">+4.2%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-data-mono text-on-surface text-sm">TSLA_AUTO</span>
                    <span className="font-data-mono text-error">-1.8%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-data-mono text-on-surface text-sm">BTC_NODE</span>
                    <span className="font-data-mono text-primary">+0.7%</span>
                  </div>
                </div>
              </div>

              {/* News Feed */}
              <div className="col-span-8 row-span-2 relative bg-surface-container-lowest/40 backdrop-blur-md rounded-xl border border-primary/20 p-5 overflow-hidden flex gap-6">
                <div className="corner-bracket cb-br" />
                <div className="w-1/3 shrink-0 rounded-lg overflow-hidden border border-primary/10 group">
                  <img
                    className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500"
                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuDltBAAYTB2drGx2sBsU5bnQzFWb_VaGJVUL1uNXbq0qPm6Dgog8EPkveABd3VfgLHK7eW59u8VqlFriw0BGVWwY-qq3ftqzz9q9aEe8gPM_ZirVfUgeOtmiVtkqZXo_GNi-Gq5fQ5yGjWgrR-M5Y2l5KSaP6IbII7YP7MrL9rYrSR-1lmc_VgRUhtnUMfSFW94GDNO52i29I86IwvqKfRxcPnUuqu8NDsqBQShpn3LgE-Oe4kxbxxvT_1lMXC2xz92jUnUw2G75P9s"
                    alt="Futuristic skyline"
                  />
                </div>
                <div className="flex flex-col justify-center">
                  <h3 className="font-label-caps text-label-caps text-primary mb-2 flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">newspaper</span> DATA_STREAM_GLOBAL
                  </h3>
                  <h2 className="font-headline-md text-headline-md text-on-surface mb-2">Breakthrough in Quantum Entanglement Signal Stability</h2>
                  <p className="font-body-md text-on-surface-variant text-sm line-clamp-2">Research labs in the European Sector report a 40% increase in data throughput using the new Reeta-4 architecture...</p>
                  <div className="mt-3 flex gap-3">
                    <span className="font-data-mono text-[10px] text-primary/60 px-2 py-1 border border-primary/20 rounded">#QUANTUM</span>
                    <span className="font-data-mono text-[10px] text-primary/60 px-2 py-1 border border-primary/20 rounded">#REETA_UPDATE</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ===== VIEW: CHAT / NEURAL LINK ===== */}
        {activePage === 'chat' && (
          <div className="view active flex-col h-full overflow-hidden relative">
            <div className="fixed inset-0 z-0" style={{ left: '288px', top: '64px', background: 'rgba(12,14,18,0.92)', backdropFilter: 'blur(16px)' }} />
            <div className="flex flex-col items-center justify-center h-full relative z-10">
              {/* Rotating Arcs */}
              <div className="absolute w-[400px] h-[400px] neural-ring border border-primary/20 rounded-full pointer-events-none" />
              <div className="absolute w-[360px] h-[360px] neural-ring border-2 border-dashed border-primary/10 rounded-full pointer-events-none" style={{ animationDirection: 'reverse', animationDuration: '15s' }} />

              {/* Voice Core */}
              <div className="relative w-48 h-48 rounded-full bg-surface-container-lowest border-2 border-primary glow-bloom flex items-center justify-center">
                <div className="absolute inset-0 rounded-full bg-primary/10 animate-pulse" />
                <span className="material-symbols-outlined text-primary text-6xl">graphic_eq</span>
                {/* Waveform */}
                <div className="absolute -inset-16 flex items-center justify-around px-8 pointer-events-none">
                  <div className="waveform-bar w-1.5 h-12 bg-primary/60 rounded-full" style={{ animationDelay: '0.1s' }} />
                  <div className="waveform-bar w-1.5 h-20 bg-primary rounded-full" style={{ animationDelay: '0.2s' }} />
                  <div className="waveform-bar w-1.5 h-32 bg-primary/40 rounded-full" style={{ animationDelay: '0.3s' }} />
                  <div className="waveform-bar w-1.5 h-24 bg-primary rounded-full" style={{ animationDelay: '0.4s' }} />
                  <div className="waveform-bar w-1.5 h-16 bg-primary/60 rounded-full" style={{ animationDelay: '0.5s' }} />
                </div>
              </div>

              {/* Transcript */}
              <div className="mt-20 text-center max-w-2xl z-10">
                <div className="inline-block px-3 py-1 bg-primary/10 border border-primary/30 rounded mb-4">
                  <span className="font-label-caps text-[10px] text-primary tracking-widest uppercase">Input Stream Active</span>
                </div>
                <div className="h-12 overflow-hidden flex items-center justify-center">
                  <p className="font-data-mono text-headline-md text-primary typewriter">REETA, CALCULATE OPTIMAL ROUTE TO SECTOR 7...</p>
                </div>
                <p className="font-label-caps text-label-caps text-on-surface-variant/50 mt-4 tracking-tighter">
                  NEURAL LATENCY: 12ms | CONFIDENCE: 98.4%
                </p>
              </div>

              {/* Flanking Left Panel: ENV_FORECAST */}
              <div className="absolute left-12 top-1/2 -translate-y-1/2 w-72 space-y-4">
                <div className="bg-surface/10 backdrop-blur-md border-l-2 border-primary/50 p-4 relative overflow-hidden group hover:bg-surface/20 transition-all">
                  <div className="hologram-border absolute inset-0 bg-primary/5" />
                  <h3 className="font-label-caps text-label-caps text-on-surface-variant mb-3">ENV_FORECAST</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-end">
                      <span className="font-data-mono text-display-lg text-primary">24°C</span>
                      <span className="font-label-caps text-[10px] text-primary/60 pb-2">STABLE</span>
                    </div>
                    <div className="w-full h-1 bg-primary/10 rounded-full overflow-hidden">
                      <div className="w-2/3 h-full bg-primary shadow-[0_0_8px_#00dbe7]" />
                    </div>
                    <div className="grid grid-cols-2 gap-2 mt-3">
                      <div className="p-2 border border-primary/10 bg-primary/5">
                        <p className="font-label-caps text-[8px] text-on-surface-variant/50 uppercase">Humidity</p>
                        <p className="font-data-mono text-label-caps text-on-surface">42.1%</p>
                      </div>
                      <div className="p-2 border border-primary/10 bg-primary/5">
                        <p className="font-label-caps text-[8px] text-on-surface-variant/50 uppercase">Visibility</p>
                        <p className="font-data-mono text-label-caps text-on-surface">14.2km</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Flanking Right Panel: ACTIVE_VECTOR */}
              <div className="absolute right-12 top-1/2 -translate-y-1/2 w-80">
                <div className="bg-surface/10 backdrop-blur-md border-r-2 border-primary/50 p-4 relative group">
                  <div className="hologram-border absolute inset-0 bg-primary/5" />
                  <div className="flex justify-between items-center mb-5">
                    <h3 className="font-label-caps text-label-caps text-on-surface-variant">ACTIVE_VECTOR</h3>
                    <span className="material-symbols-outlined text-secondary animate-pulse text-sm">near_me</span>
                  </div>
                  <div className="relative pl-6 space-y-5 before:content-[''] before:absolute before:left-2 before:top-2 before:bottom-2 before:w-px before:bg-primary/20">
                    <div className="relative">
                      <div className="absolute -left-[1.2rem] top-1.5 w-2 h-2 rounded-full bg-primary border border-primary-container" />
                      <p className="font-label-caps text-[10px] text-on-surface-variant/60 uppercase">Origin</p>
                      <p className="font-data-mono text-body-md text-on-surface">NEURAL_HUB_ALPHA</p>
                    </div>
                    <div className="flex items-center gap-4 py-2 border-y border-primary/5">
                      <div className="flex-1">
                        <p className="font-label-caps text-[8px] text-secondary uppercase">ETA ESTIMATE</p>
                        <p className="font-data-mono text-headline-md text-secondary">08:42<span className="text-sm">m</span></p>
                      </div>
                      <div className="w-12 h-12 rounded bg-secondary/10 flex items-center justify-center">
                        <span className="material-symbols-outlined text-secondary">schedule</span>
                      </div>
                    </div>
                    <div className="relative">
                      <div className="absolute -left-[1.2rem] top-1.5 w-2 h-2 rounded-full bg-surface border border-primary" />
                      <p className="font-label-caps text-[10px] text-on-surface-variant/60 uppercase">Destination</p>
                      <p className="font-data-mono text-body-md text-on-surface">SECTOR_7_GATE</p>
                    </div>
                  </div>
                  <div className="mt-5">
                    <img
                      className="w-full h-28 object-cover rounded border border-primary/20 grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-700"
                      src="https://lh3.googleusercontent.com/aida-public/AB6AXuChWsm-hvQL-5owHJ21uzTpCTi_5FzhzvmSnI2J170C6PF2CoREisUT-3qRkc8GGXEyw89RNlIW0Qgz16whVg-RunVN_Qcn7TGdZS6giPNOHo-6obuRAV-RTYSgGnVu3h3VRGprj1PsIhJl-iTdzbJuQarO7AR4IGlB4gR8FfpcWXrnk03_U0LM_nR2WI2UkY2Ef8FgkyZ72hrUvZOt_2jlhHu9Rwicn8aVbjBHjvg28xvAo0jxQmd6GCfSl7NL01Bf9Fh7hIm-8FqD"
                      alt="Futuristic city map"
                    />
                  </div>
                </div>
              </div>

              {/* Controls */}
              <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex items-center gap-8 z-20">
                <button onClick={() => setActivePage('home')} className="w-12 h-12 rounded-full border border-error/50 flex items-center justify-center text-error hover:bg-error/10 transition-all group cursor-pointer">
                  <span className="material-symbols-outlined group-hover:scale-110 transition-transform">close</span>
                </button>
                <div className="px-8 py-3 bg-surface-container/30 backdrop-blur-xl border border-primary/20 rounded-full flex items-center gap-6">
                  <span className="material-symbols-outlined text-primary cursor-pointer hover:scale-110 transition-transform">mic_off</span>
                  <div className="h-4 w-px bg-primary/20" />
                  <span className="material-symbols-outlined text-on-surface-variant/50 cursor-pointer hover:text-primary transition-colors">volume_up</span>
                  <div className="h-4 w-px bg-primary/20" />
                  <span className="material-symbols-outlined text-on-surface-variant/50 cursor-pointer hover:text-primary transition-colors">settings</span>
                </div>
                <button onClick={() => setActivePage('automation')} className="w-12 h-12 rounded-full border border-secondary/50 flex items-center justify-center text-secondary hover:bg-secondary/10 transition-all group cursor-pointer">
                  <span className="material-symbols-outlined group-hover:rotate-90 transition-transform">sync</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ===== VIEW: WORLD SNAPSHOT ===== */}
        {activePage === 'world' && (
          <div className="view active flex-col h-full p-5 overflow-hidden gap-4">
            <div className="flex-1 grid grid-cols-12 gap-5 overflow-hidden">
              {/* Column 1: News */}
              <section className="col-span-3 flex flex-col h-full overflow-hidden">
                <div className="flex items-center justify-between mb-3 border-b border-primary/20 pb-2">
                  <h3 className="font-label-caps text-primary/90 flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">rss_feed</span> GLOBAL_INTEL
                  </h3>
                  <span className="font-data-mono text-[10px] text-primary/40">LIVE_FEED</span>
                </div>
                <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                  {[
                    { time: 'T+ 00:04:12', text: 'Quantum decryptor nodes identified in Subsector 7G. Surveillance active.' },
                    { time: 'T+ 00:12:45', text: 'Neural network expansion reached 94% coverage across Pacific Hub.' },
                    { time: 'T+ 00:31:02', text: "Satellite 'Aether-1' reports anomalous solar flares affecting long-range comms." },
                    { time: 'T+ 01:05:19', text: 'Atmospheric scrubbing protocols initiated in Neo-Tokyo district.' },
                    { time: 'T+ 01:45:33', text: 'Core temperature stabilized at 3.4 Kelvin. Cooling cycles complete.' }
                  ].map((item, idx) => (
                    <div key={idx} className="relative pl-4 hologram-panel p-3 group cursor-pointer hover:bg-primary/5 transition-all">
                      <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary-container shadow-[0_0_8px_rgba(0,219,231,0.8)]" />
                      <div className="font-data-mono text-[10px] text-primary/40 mb-1">{item.time}</div>
                      <p className="text-sm font-body-md text-primary/90 leading-snug">{item.text}</p>
                    </div>
                  ))}
                </div>
              </section>

              {/* Column 2: Market Charts */}
              <section className="col-span-5 flex flex-col h-full">
                <div className="flex items-center justify-between mb-3 border-b border-primary/20 pb-2">
                  <h3 className="font-label-caps text-primary/90 flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">show_chart</span> MARKET_VECTORS
                  </h3>
                  <div className="flex gap-4">
                    <span className="font-data-mono text-[10px] text-primary-container">▲ 0.42% AGGR</span>
                    <span className="font-data-mono text-[10px] text-primary/40">REAL_TIME</span>
                  </div>
                </div>
                <div className="hologram-panel relative flex-1 mb-5 rounded-lg overflow-hidden group">
                  <div className="corner-bracket cb-tl" /><div className="corner-bracket cb-tr" />
                  <div className="corner-bracket cb-bl" /><div className="corner-bracket cb-br" />
                  <div className="absolute inset-x-8 inset-y-12 flex items-end justify-between gap-1 overflow-hidden">
                    <div className="w-full bg-primary/20 rounded-t animate-[pulse_3s_infinite]" style={{ height: '65%' }} />
                    <div className="w-full bg-primary/10 rounded-t animate-[pulse_4s_infinite]" style={{ height: '45%' }} />
                    <div className="w-full bg-primary-container/40 rounded-t shadow-[0_0_15px_rgba(0,242,255,0.3)] animate-[pulse_2s_infinite]" style={{ height: '85%' }} />
                    <div className="w-full bg-primary/20 rounded-t animate-[pulse_5s_infinite]" style={{ height: '35%' }} />
                    <div className="w-full bg-primary/10 rounded-t animate-[pulse_3s_infinite]" style={{ height: '55%' }} />
                    <div className="w-full bg-secondary/20 rounded-t animate-[pulse_6s_infinite]" style={{ height: '75%' }} />
                    <div className="w-full bg-primary/20 rounded-t animate-[pulse_4s_infinite]" style={{ height: '40%' }} />
                    <div className="w-full bg-primary-container/40 rounded-t shadow-[0_0_15px_rgba(0,242,255,0.3)] animate-[pulse_2.5s_infinite]" style={{ height: '95%' }} />
                  </div>
                  <div className="absolute top-4 left-6">
                    <span className="font-data-mono text-lg text-primary font-bold">REETA_INDEX_V4</span>
                    <span className="block font-data-mono text-[10px] text-primary/40">COMPOSITE SYNTHETIC ASSETS</span>
                  </div>
                  <div className="absolute bottom-4 right-6 text-right">
                    <span className="font-data-mono text-2xl text-primary-container">14,289.42</span>
                    <div className="font-data-mono text-[10px] text-secondary">HODL_MANTRA: OPTIMAL</div>
                  </div>
                </div>
              </section>

              {/* Column 3: Navigation/Targeting */}
              <section className="col-span-4 flex flex-col h-full">
                <div className="flex items-center justify-between mb-3 border-b border-primary/20 pb-2">
                  <h3 className="font-label-caps text-primary/90 flex items-center gap-2">
                    <span className="material-symbols-outlined text-sm">navigation</span> TRAJECTORY_MOD
                  </h3>
                  <span className="font-data-mono text-[10px] text-primary/40">GNSS_LOCKED</span>
                </div>
                <div className="hologram-panel p-4 mb-4 space-y-4">
                  <div className="space-y-1">
                    <label className="font-label-caps text-[10px] text-primary/60">ORIGIN_COORDINATES</label>
                    <div className="flex items-center border-b border-primary/20 py-1 focus-within:border-primary-container transition-all">
                      <span className="font-data-mono text-primary-container mr-2 text-xs">&gt;</span>
                      <input className="bg-transparent border-none outline-none font-data-mono text-xs w-full text-primary placeholder-primary/20 p-0" type="text" defaultValue="35.6895° N, 139.6917° E" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="font-label-caps text-[10px] text-primary/60">TARGET_COORDINATES</label>
                    <div className="flex items-center border-b border-primary/20 py-1 focus-within:border-primary-container transition-all">
                      <span className="font-data-mono text-primary-container mr-2 text-xs">&gt;</span>
                      <input className="bg-transparent border-none outline-none font-data-mono text-xs w-full text-primary placeholder-primary/20 p-0" placeholder="ENTER TARGET_ID..." type="text" />
                      <span className="font-data-mono text-primary animate-pulse text-xs">_</span>
                    </div>
                  </div>
                  <button className="w-full py-2 bg-primary/5 border border-primary/30 hover:bg-primary/20 font-label-caps text-[11px] text-primary transition-all cursor-pointer">CALCULATE_OPTIMAL_VECT</button>
                </div>
                <div className="flex-1 hologram-panel relative rounded-lg overflow-hidden p-6 flex flex-col items-center justify-center">
                  <div className="corner-bracket cb-tl opacity-40" />
                  <div className="corner-bracket cb-tr opacity-40" />
                  <div className="absolute w-64 h-64 border border-primary/10 rounded-full animate-[spin_20s_linear_infinite]" />
                  <div className="absolute w-56 h-56 border border-primary/5 border-dashed rounded-full animate-[spin_15s_linear_infinite_reverse]" />
                  <div className="absolute w-40 h-40 border border-primary/20 rounded-full flex items-center justify-center">
                    <div className="w-1 h-1 bg-primary-container shadow-[0_0_10px_rgba(0,242,255,1)] rounded-full" />
                  </div>
                  <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 200 200">
                    <path d="M 100,100 m -60,0 a 60,60 0 1,1 120,0 a 60,60 0 1,1 -120,0" fill="none" stroke="rgba(0,219,231,0.2)" strokeDasharray="2,4" strokeWidth="0.5" />
                    <path className="animate-pulse" d="M 50,50 Q 100,10 150,50" fill="none" stroke="rgba(0,219,231,0.4)" strokeWidth="1.5" />
                    <path d="M 40,150 Q 100,190 160,150" fill="none" stroke="rgba(254,216,58,0.3)" strokeWidth="1.5" />
                  </svg>
                  <div className="absolute top-4 right-4 text-right">
                    <div className="font-data-mono text-[9px] text-primary/50">ALTITUDE</div>
                    <div className="font-data-mono text-xs text-primary">34,000 FT</div>
                  </div>
                  <div className="absolute bottom-4 left-4">
                    <div className="font-data-mono text-[9px] text-primary/50">SIGNAL_STRENGTH</div>
                    <div className="flex gap-1 mt-1">
                      <div className="w-1 h-3 bg-primary-container" />
                      <div className="w-1 h-3 bg-primary-container" />
                      <div className="w-1 h-3 bg-primary-container" />
                      <div className="w-1 h-3 bg-primary/20" />
                      <div className="w-1 h-3 bg-primary/20" />
                    </div>
                  </div>
                  <div className="relative z-10 text-center">
                    <div className="font-label-caps text-lg tracking-[0.2em] mb-1">SCANNING...</div>
                    <div className="font-data-mono text-[10px] text-primary/60">SYNCING WITH ORBITAL ARRAY</div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        )}

        {/* ===== VIEW: AUTOMATION ===== */}
        {activePage === 'automation' && (
          <div className="view active flex-col h-full overflow-hidden">
            <main className="flex flex-1 gap-6 h-full p-6 overflow-hidden">
              <section className="flex-1 relative flex items-center justify-center">
                <div className="absolute inset-0 pointer-events-none opacity-20">
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] border border-primary/30 rounded-full" />
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] border border-primary/10 rounded-full border-dashed" />
                </div>
                <div className="grid grid-cols-4 gap-4 p-8 relative">
                  <div className="absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-primary/60" />
                  <div className="absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-primary/60" />
                  <div className="absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-primary/60" />
                  <div className="absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-primary/60" />

                  {[
                    { label: 'OPEN APP', icon: 'open_in_new', mt: '' },
                    { label: 'WEB SEARCH', icon: 'search', mt: 'mt-12' },
                    { label: 'CLOSE APP', icon: 'close', mt: '' },
                    { label: 'EMERGENCY STOP', icon: 'warning', mt: 'mt-12', color: 'text-secondary' },
                    { label: 'DATA SYNC', icon: 'cloud_upload', mt: '' },
                    { label: 'EXECUTE SCRIPT', icon: 'terminal', mt: 'mt-12' }
                  ].map((item, idx) => (
                    <div
                      key={idx}
                      onClick={() => handleHexClick(item.label)}
                      className={`hexagon auto-hex group flex flex-col items-center justify-center w-40 h-44 bg-surface-container/20 border border-primary/30 cursor-pointer p-4 text-center ${item.mt}`}
                    >
                      <span className={`material-symbols-outlined text-3xl mb-2 ${item.color || 'text-primary'} group-hover:scale-110 transition-transform`}>
                        {item.icon}
                      </span>
                      <span className="font-label-caps text-[10px] tracking-tighter">{item.label}</span>
                      <div className="mt-2 w-10 h-0.5 bg-primary/20 group-hover:bg-primary transition-colors" />
                    </div>
                  ))}
                </div>
              </section>

              <aside className="w-80 h-full flex flex-col bg-surface-container-low/30 backdrop-blur-sm border-l border-primary/10">
                <div className="p-4 border-b border-primary/10 flex justify-between items-center bg-surface-container/50">
                  <h3 className="font-label-caps text-label-caps text-primary">ACTIVITY_LOG.TXT</h3>
                  <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                </div>
                <div ref={terminalRef} className="flex-1 p-4 font-data-mono text-data-mono text-on-surface-variant/80 terminal-scroll overflow-y-auto space-y-3">
                  {logs.map((log) => (
                    <div
                      key={log.id}
                      className={`border-l-2 pl-3 ${
                        log.type === 'override'
                          ? 'border-primary/70 font-bold text-primary'
                          : log.type === 'cmd'
                          ? 'border-secondary/60 text-secondary'
                          : log.type === 'accent'
                          ? 'border-secondary/60'
                          : 'border-primary/30'
                      }`}
                    >
                      <span className="text-primary/60">[{log.time}]</span> {log.msg}
                    </div>
                  ))}
                </div>
                <div className="p-4 border-t border-primary/10 bg-surface-container-lowest/50">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-1.5 h-4 bg-primary animate-pulse" />
                    <span className="font-label-caps text-[10px] text-primary/40 uppercase">Awaiting Command...</span>
                  </div>
                  <input
                    value={cmdInput}
                    onChange={(e) => setCmdInput(e.target.value)}
                    onKeyDown={handleCmdSubmit}
                    className="w-full bg-transparent border-0 border-b border-primary/30 focus:ring-0 focus:border-primary text-data-mono text-xs p-1 text-primary placeholder-primary/20 outline-none"
                    placeholder="type /help for commands"
                    type="text"
                  />
                </div>
              </aside>
            </main>

            <footer className="h-12 border-t border-primary/10 flex items-center px-8 gap-10 bg-surface-container-lowest/80 backdrop-blur-xl shrink-0">
              <div className="flex gap-2 items-center">
                <span className="font-label-caps text-[10px] text-primary/60">CPU:</span>
                <div className="w-20 h-1.5 bg-surface-container-highest rounded-full">
                  <div className="h-full bg-primary" style={{ width: `${cpuUsage}%` }} />
                </div>
                <span className="font-data-mono text-[10px]">{cpuUsage}%</span>
              </div>
              <div className="flex gap-2 items-center">
                <span className="font-label-caps text-[10px] text-primary/60">RAM:</span>
                <div className="w-20 h-1.5 bg-surface-container-highest rounded-full">
                  <div className="h-full bg-primary w-[62%]" />
                </div>
                <span className="font-data-mono text-[10px]">16.4 GB</span>
              </div>
              <div className="ml-auto font-data-mono text-[10px] text-primary/40 flex items-center gap-4">
                <span className="flex items-center gap-1"><span className="material-symbols-outlined text-xs">wifi</span> 128.0.0.1</span>
                <span className="flex items-center gap-1"><span className="material-symbols-outlined text-xs">schedule</span> UTC +05:30</span>
              </div>
            </footer>
          </div>
        )}

        {/* ===== VIEW: PROFILE ===== */}
        {activePage === 'profile' && (
          <div className="view active flex-col items-center justify-center h-full">
            <div className="relative flex flex-col items-center gap-8 max-w-lg w-full px-8">
              <div className="relative w-36 h-36">
                <div className="hexagon w-full h-full bg-primary/10 border-2 border-primary/60 glow-cyan flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary text-6xl" style={{ fontVariationSettings: "'FILL' 1" }}>account_circle</span>
                </div>
              </div>
              <div className="text-center">
                <h2 className="font-display-lg text-display-lg-mobile text-primary text-glow">REETA NODE-04</h2>
                <p className="font-label-caps text-label-caps text-on-surface-variant/60 mt-1">OPERATOR: NISHANKA — CLEARANCE: ALPHA-7</p>
              </div>
              <button onClick={() => setActivePage('home')} className="w-full py-3 border border-primary/40 rounded-lg font-label-caps text-label-caps text-primary hover:bg-primary/10 transition-all cursor-pointer">
                ← RETURN TO HUD
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

