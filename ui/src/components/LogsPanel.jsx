/**
 * ==================================================
 * REETA — ui/src/components/LogsPanel.jsx
 * ==================================================
 * PURPOSE:
 *   Displays real-time backend logs in a terminal-style panel.
 *
 * PHASE 4.5 HARDENING:
 *   - LogEntry is wrapped in React.memo to prevent re-renders
 *     of existing log rows when new ones arrive.
 *   - Auto-scroll uses requestAnimationFrame to avoid layout
 *     thrashing during rapid log bursts.
 * ==================================================
 */

import React, { useRef, useEffect, useCallback, memo } from 'react';
import useStore from '../store/useStore';
import { Terminal, AlertCircle, Info, AlertTriangle, Trash2 } from 'lucide-react';

// Memoized individual log row — only re-renders if its own data changes
const LogEntry = memo(({ log }) => {
  const getLogIcon = (level) => {
    switch (level) {
      case 'ERROR': return <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />;
      case 'WARNING': return <AlertTriangle className="w-4 h-4 text-yellow-500 shrink-0" />;
      default: return <Info className="w-4 h-4 text-blue-400 shrink-0" />;
    }
  };

  const getLogColor = (level) => {
    switch (level) {
      case 'ERROR': return 'text-red-400';
      case 'WARNING': return 'text-yellow-400';
      default: return 'text-gray-300';
    }
  };

  let timeStr = '';
  try {
    timeStr = new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch {
    timeStr = '--:--:--';
  }

  return (
    <div className="flex gap-3 hover:bg-gray-800/50 p-1 rounded transition-colors">
      <span className="text-gray-600 shrink-0">{timeStr}</span>
      {getLogIcon(log.level)}
      <div className="flex flex-col gap-1 w-full overflow-hidden">
        <span className={`break-words ${getLogColor(log.level)}`}>
          <span className="text-gray-500 mr-2">[{log.module}]</span>
          {log.message}
        </span>
        {log.exception && (
          <pre className="mt-1 bg-red-950/30 text-red-300 p-2 rounded border border-red-900/50 overflow-x-auto whitespace-pre-wrap">
            {log.exception}
          </pre>
        )}
      </div>
    </div>
  );
});

LogEntry.displayName = 'LogEntry';

const LogsPanel = () => {
  const logs = useStore((state) => state.logs);
  const clearLogs = useStore((state) => state.clearLogs);
  const wsConnected = useStore((state) => state.wsConnected);
  const logsEndRef = useRef(null);

  // Use requestAnimationFrame for scroll to avoid layout thrashing
  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [logs, scrollToBottom]);

  return (
    <div className="bg-[#0D1117] rounded-xl shadow-xl border border-gray-800 h-full flex flex-col overflow-hidden font-mono text-xs">
      <div className="bg-[#161B22] p-3 border-b border-gray-800 flex justify-between items-center">
        <h2 className="text-gray-200 font-semibold flex items-center gap-2 text-sm font-sans">
          <Terminal className="w-4 h-4 text-gray-400" />
          System Diagnostics
          <span className="text-xs text-gray-500 font-normal ml-2">({logs.length})</span>
        </h2>
        <div className="flex items-center gap-3">
          <button 
            onClick={clearLogs}
            className="text-gray-500 hover:text-gray-300 transition-colors"
            title="Clear logs"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          <span className="flex h-2 w-2 relative">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${wsConnected ? 'bg-green-400' : 'bg-red-400'}`}></span>
            <span className={`relative inline-flex rounded-full h-2 w-2 ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
          </span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-1.5 custom-scrollbar">
        {logs.length === 0 ? (
          <div className="text-gray-600 italic">Waiting for system logs...</div>
        ) : (
          logs.map((log, i) => <LogEntry key={i} log={log} />)
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
};

export default LogsPanel;
