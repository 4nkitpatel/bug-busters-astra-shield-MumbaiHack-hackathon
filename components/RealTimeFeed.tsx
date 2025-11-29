
import React from 'react';
import { Claim, Verdict } from '../types';

interface RealTimeFeedProps {
  claims: Claim[];
}

const RealTimeFeed: React.FC<RealTimeFeedProps> = ({ claims }) => {
  const getSourceIcon = (source: string) => {
    const s = source.toLowerCase();
    if (s.includes('twitter') || s.includes('x.com')) return 'fab fa-twitter text-cyan-400';
    if (s.includes('facebook')) return 'fab fa-facebook text-blue-500';
    if (s.includes('whatsapp')) return 'fab fa-whatsapp text-green-500';
    return 'fas fa-newspaper text-slate-400';
  };

  const getStatusBadge = (status: string, verdict?: Verdict) => {
    if (status === 'DETECTING' || status === 'VERIFYING') {
      return (
        <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-mono text-cyan-400 animate-pulse">
          <i className="fas fa-circle-notch fa-spin text-[8px]"></i>
          <span>{status}</span>
        </span>
      );
    }
    if (verdict === Verdict.SAFE) {
      return <span className="px-2 py-0.5 rounded-full bg-emerald-900/30 border border-emerald-500/30 text-[10px] font-bold text-emerald-400">VERIFIED SAFE</span>;
    }
    if (verdict === Verdict.SCAM || verdict === Verdict.SUSPICIOUS) {
      return <span className="px-2 py-0.5 rounded-full bg-red-900/30 border border-red-500/30 text-[10px] font-bold text-red-400">DEBUNKED</span>;
    }
    return null;
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4 px-2">
         <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
           <i className="fas fa-satellite-dish mr-2 text-cyan-500 animate-pulse"></i>
           Live Claim Stream
         </h3>
         <div className="flex space-x-2 text-[10px] font-mono text-slate-500">
            <span className="flex items-center"><div className="w-1.5 h-1.5 rounded-full bg-green-500 mr-1"></div> Safe</span>
            <span className="flex items-center"><div className="w-1.5 h-1.5 rounded-full bg-red-500 mr-1"></div> Threat</span>
         </div>
      </div>

      <div className="relative flex-grow overflow-hidden mask-linear-fade">
        <div className="absolute inset-0 overflow-y-auto no-scrollbar space-y-3 pb-4">
          {claims.length === 0 && (
             <div className="text-center text-slate-500 text-xs py-10 flex flex-col items-center">
                <i className="fas fa-circle-notch fa-spin mb-2"></i>
                Connecting to Global News Network...
             </div>
          )}
          {claims.map((claim) => (
            <a 
              key={claim.id}
              href={claim.url || '#'}
              target={claim.url ? "_blank" : "_self"}
              rel="noopener noreferrer"
              className={`block p-3 rounded-xl border transition-all duration-500 animate-slide-in group cursor-pointer
                ${claim.isUserSubmission 
                  ? 'bg-cyan-950/20 border-cyan-500/50 shadow-[0_0_15px_rgba(34,211,238,0.1)]' 
                  : 'bg-slate-900/40 border-slate-800 hover:bg-slate-800/80 hover:border-slate-700'}
              `}
            >
              <div className="flex items-start justify-between mb-1">
                <div className="flex items-center space-x-2">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center bg-slate-800 text-xs group-hover:bg-slate-700 transition-colors`}>
                    <i className="fas fa-user-secret text-slate-500 group-hover:text-cyan-400"></i>
                  </div>
                  <div className="flex flex-col">
                     <span className="text-[10px] font-bold text-slate-400 flex items-center gap-1">
                        {claim.isUserSubmission ? 'Anonymous User' : claim.source}
                        <i className={`${getSourceIcon(claim.source)} ml-1`}></i>
                     </span>
                  </div>
                </div>
                <div className="flex flex-col items-end">
                  <span className="text-[10px] font-mono text-slate-500">{claim.timestamp}</span>
                  {claim.engagementSpike && (
                    <span className="text-[9px] font-bold text-amber-400 flex items-center">
                       <i className="fas fa-chart-line mr-1"></i> {claim.engagementSpike}
                    </span>
                  )}
                </div>
              </div>

              <p className="text-xs text-slate-200 mb-2 font-medium leading-relaxed pl-8 group-hover:text-white transition-colors">
                {claim.text}
                {claim.url && <i className="fas fa-external-link-alt ml-2 text-[9px] text-slate-600 group-hover:text-cyan-500"></i>}
              </p>

              <div className="flex items-center justify-between pl-8">
                 {getStatusBadge(claim.status, claim.verdict)}
                 
                 {claim.riskScore !== undefined && (
                   <div className="text-[10px] font-mono text-slate-500">
                     Risk: <span className={claim.riskScore > 50 ? 'text-red-400' : 'text-emerald-400'}>{claim.riskScore}/100</span>
                   </div>
                 )}
              </div>
            </a>
          ))}
        </div>
      </div>
      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-slide-in {
          animation: slideIn 0.4s ease-out forwards;
        }
        .mask-linear-fade {
          mask-image: linear-gradient(to bottom, black 90%, transparent 100%);
        }
      `}</style>
    </div>
  );
};

export default RealTimeFeed;
