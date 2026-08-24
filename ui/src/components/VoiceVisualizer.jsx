import React from 'react';
import { motion } from 'framer-motion';
import useStore from '../store/useStore';
import { Mic, MicOff, Brain, Volume2 } from 'lucide-react';

const VoiceVisualizer = () => {
  const voiceState = useStore((state) => state.voiceState);
  const wsConnected = useStore((state) => state.wsConnected);

  // Define animation profiles based on the state
  const getAnimationProps = () => {
    switch (voiceState) {
      case 'listening':
        return { height: ["20%", "80%", "40%", "100%", "30%"], transition: { repeat: Infinity, duration: 0.6, ease: "easeInOut" } };
      case 'processing':
        return { height: ["100%", "20%"], transition: { repeat: Infinity, duration: 1.2, ease: "easeInOut", repeatType: "mirror" } };
      case 'speaking':
        return { height: ["30%", "90%", "50%", "100%", "20%"], transition: { repeat: Infinity, duration: 0.4, ease: "easeInOut" } };
      default: // idle
        return { height: "10%", transition: { duration: 0.5 } };
    }
  };

  const getStateColor = () => {
    if (!wsConnected) return 'text-red-500';
    switch (voiceState) {
      case 'listening': return 'text-green-400';
      case 'processing': return 'text-yellow-400';
      case 'speaking': return 'text-blue-400';
      default: return 'text-gray-500';
    }
  };

  const getStatusText = () => {
    if (!wsConnected) return "Disconnected from backend";
    switch (voiceState) {
      case 'listening': return "Listening...";
      case 'processing': return "Thinking...";
      case 'speaking': return "Speaking...";
      default: return "Idle (Say 'Hey REETA')";
    }
  };

  const getIcon = () => {
    if (!wsConnected) return <MicOff className="w-5 h-5 text-red-500" />;
    switch (voiceState) {
      case 'listening': return <Mic className="w-5 h-5 text-green-400 animate-pulse" />;
      case 'processing': return <Brain className="w-5 h-5 text-yellow-400 animate-pulse" />;
      case 'speaking': return <Volume2 className="w-5 h-5 text-blue-400 animate-pulse" />;
      default: return <Mic className="w-5 h-5 text-gray-500" />;
    }
  };

  const bars = Array.from({ length: 9 });

  return (
    <div className="bg-gray-800 rounded-xl p-6 shadow-xl border border-gray-700 flex flex-col items-center justify-center min-h-[160px] relative overflow-hidden">
      
      {/* Background Glow */}
      <div className={`absolute inset-0 opacity-10 transition-colors duration-500 ${
        voiceState === 'listening' ? 'bg-green-500' :
        voiceState === 'processing' ? 'bg-yellow-500' :
        voiceState === 'speaking' ? 'bg-blue-500' : 'bg-transparent'
      }`} />

      <div className="flex items-center gap-3 mb-6 z-10">
        <div className="p-2 bg-gray-900 rounded-full shadow-inner border border-gray-700">
          {getIcon()}
        </div>
        <span className={`font-semibold tracking-wide ${getStateColor()}`}>
          {getStatusText()}
        </span>
      </div>

      <div className="flex gap-2 items-end h-12 w-full justify-center z-10 px-8">
        {bars.map((_, i) => (
          <motion.div
            key={i}
            className={`w-3 rounded-full ${
              voiceState === 'listening' ? 'bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.6)]' :
              voiceState === 'processing' ? 'bg-yellow-400 shadow-[0_0_8px_rgba(250,204,21,0.6)]' :
              voiceState === 'speaking' ? 'bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.6)]' : 
              'bg-gray-600'
            }`}
            animate={getAnimationProps()}
            initial={{ height: "10%" }}
            style={{ 
              animationDelay: `${i * 0.1}s` 
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default VoiceVisualizer;
