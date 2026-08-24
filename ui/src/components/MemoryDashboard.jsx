import React from 'react';
import useStore from '../store/useStore';
import { Database, Search } from 'lucide-react';

const MemoryDashboard = () => {
  const memories = useStore((state) => state.memories);

  return (
    <div className="bg-gray-900 rounded-xl shadow-xl border border-gray-800 h-full flex flex-col overflow-hidden">
      <div className="bg-gray-800 p-4 border-b border-gray-700 flex justify-between items-center">
        <h2 className="text-gray-100 font-semibold flex items-center gap-2">
          <Database className="w-5 h-5 text-purple-400" />
          Memory Core
        </h2>
        <div className="relative">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
          <input 
            type="text" 
            placeholder="Search memories..."
            className="bg-gray-900 text-sm text-gray-200 rounded-full pl-9 pr-4 py-1.5 border border-gray-700 focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {memories.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-3">
            <Database className="w-12 h-12 opacity-20" />
            <p>No memories currently in working context.</p>
          </div>
        ) : (
          memories.map((mem, i) => (
            <div key={i} className="p-3 bg-gray-800 rounded-lg border border-gray-700 hover:border-purple-500/50 transition-colors group">
              <div className="flex justify-between items-start mb-1">
                <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider">{mem.category || 'General'}</span>
                <span className="text-xs text-gray-500">{mem.timestamp || 'Just now'}</span>
              </div>
              <p className="text-sm text-gray-300">{mem.content}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MemoryDashboard;
