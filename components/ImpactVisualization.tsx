
import React from 'react';

const ImpactVisualization: React.FC = () => {
  const impacts = [
    {
      title: "Mumbai Flood Rumor",
      before: "24K Shares",
      after: "Reach -94%",
      icon: "fa-water"
    },
    {
      title: "Fake Relief QR",
      before: "850 Reports",
      after: "Wallet Frozen",
      icon: "fa-qrcode"
    },
    {
      title: "Old Photo Reshare",
      before: "Viral",
      after: "Flagged",
      icon: "fa-image"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
      {impacts.map((item, idx) => (
        <div key={idx} className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 flex items-center justify-between group hover:bg-slate-900/60 transition-all">
           <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-cyan-400 group-hover:scale-110 transition-all">
                <i className={`fas ${item.icon}`}></i>
              </div>
              <div>
                 <div className="text-xs font-bold text-slate-300">{item.title}</div>
                 <div className="text-[10px] text-slate-500 mt-0.5">BEFORE: <span className="text-red-400">{item.before}</span></div>
              </div>
           </div>
           <div className="text-right">
              <div className="text-xs font-bold text-emerald-400 bg-emerald-900/20 px-2 py-1 rounded border border-emerald-500/20">
                 {item.after}
              </div>
           </div>
        </div>
      ))}
    </div>
  );
};

export default ImpactVisualization;
