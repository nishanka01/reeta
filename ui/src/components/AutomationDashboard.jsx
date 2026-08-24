import React from 'react';
import useStore from '../store/useStore';
import { Activity, PlayCircle, CheckCircle2, Circle } from 'lucide-react';
import { motion } from 'framer-motion';

const AutomationDashboard = () => {
  const activeWorkflow = useStore((state) => state.activeWorkflow);
  const workflowSteps = useStore((state) => state.workflowSteps);

  return (
    <div className="bg-gray-900 rounded-xl shadow-xl border border-gray-800 h-full flex flex-col overflow-hidden">
      <div className="bg-gray-800 p-4 border-b border-gray-700 flex justify-between items-center">
        <h2 className="text-gray-100 font-semibold flex items-center gap-2">
          <Activity className="w-5 h-5 text-green-400" />
          Active Workflows
        </h2>
        {activeWorkflow && (
          <span className="flex items-center gap-2 text-xs text-green-400 bg-green-400/10 px-2 py-1 rounded-full border border-green-400/20 animate-pulse">
            <PlayCircle className="w-3 h-3" /> Running
          </span>
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto p-5">
        {!activeWorkflow ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-3">
            <Activity className="w-12 h-12 opacity-20" />
            <p>No automation tasks currently running.</p>
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-200 mb-1">{activeWorkflow.title || "Executing Workflow"}</h3>
              <p className="text-sm text-gray-400">REETA has taken control of the desktop to complete this task.</p>
            </div>
            
            <div className="space-y-4 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-700 before:to-transparent">
              {workflowSteps.map((step, index) => (
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  key={index} 
                  className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active"
                >
                  <div className={`flex items-center justify-center w-6 h-6 rounded-full border-4 border-gray-900 bg-gray-800 text-gray-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 ${
                    step.status === 'completed' ? 'text-green-500 border-green-500/30' :
                    step.status === 'running' ? 'text-blue-500 border-blue-500/30 animate-pulse' : ''
                  }`}>
                    {step.status === 'completed' ? <CheckCircle2 className="w-3 h-3" /> : <Circle className="w-3 h-3" />}
                  </div>
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-gray-700 bg-gray-800 shadow">
                    <div className="flex items-center justify-between space-x-2 mb-1">
                      <div className="font-bold text-gray-200">{step.action}</div>
                      <div className={`text-xs ${
                        step.status === 'completed' ? 'text-green-400' :
                        step.status === 'running' ? 'text-blue-400' : 'text-gray-500'
                      }`}>
                        {step.status}
                      </div>
                    </div>
                    <div className="text-sm text-gray-400">Target: {step.target}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AutomationDashboard;
