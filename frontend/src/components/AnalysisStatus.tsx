import React from 'react';

interface AnalysisStatusProps {
  status: 'idle' | 'analyzing' | 'complete' | 'error';
  step: string;
}

const AnalysisStatus: React.FC<AnalysisStatusProps> = ({ status, step }) => {
  if (status !== 'analyzing') return null;

  return (
    <div className="w-full max-w-2xl mx-auto mt-8 p-6 bg-slate-900/50 border border-slate-700 rounded-xl backdrop-blur-sm relative overflow-hidden">
      {/* Scanning Effect */}
      <div className="absolute top-0 left-0 w-full h-1 bg-cyan-500 shadow-[0_0_15px_rgba(34,211,238,0.8)] animate-[scan_2s_ease-in-out_infinite]"></div>

      <div className="flex flex-col items-center justify-center space-y-4">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-slate-700 border-t-cyan-500 rounded-full animate-spin"></div>
          <i className="fas fa-shield-alt absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-cyan-500 text-xl"></i>
        </div>
        
        <h3 className="text-xl font-mono text-cyan-400 font-bold tracking-widest">
          SYSTEM ACTIVE
        </h3>
        
        <div className="space-y-2 w-full text-center">
            <p className="text-slate-300 font-mono text-sm uppercase tracking-wide animate-pulse">
                {step}
            </p>
            <div className="flex justify-center gap-1">
                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce delay-150"></div>
                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce delay-300"></div>
            </div>
        </div>
        
        {/* Decorative Code Lines */}
        <div className="w-full text-xs font-mono text-slate-600 mt-4 opacity-50">
            <p>{`> initializing_vision_module... OK`}</p>
            <p>{`> connecting_to_search_grid... OK`}</p>
            <p>{`> running_forensic_heuristics... PENDING`}</p>
        </div>
      </div>
    </div>
  );
};

export default AnalysisStatus;

