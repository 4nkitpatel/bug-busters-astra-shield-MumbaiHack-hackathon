
import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface StatsPanelProps {
  stats: {
    monitored: number;
    verifying: number;
    debunked: number;
  };
  chartData: any[];
}

const StatsPanel: React.FC<StatsPanelProps> = ({ stats, chartData }) => {
  return (
    <div className="h-full flex flex-col space-y-6">
      
      {/* Top Counters */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-slate-900/50 border border-slate-800 p-3 rounded-lg relative overflow-hidden group hover:border-cyan-500/30 transition-colors">
           <div className="text-[10px] uppercase text-slate-500 font-bold tracking-wider mb-1">Claims Monitored</div>
           <div className="text-2xl font-mono text-white font-bold">{stats.monitored.toLocaleString()}</div>
           <i className="fas fa-globe absolute -bottom-2 -right-2 text-4xl text-slate-800 group-hover:text-cyan-900 transition-colors"></i>
        </div>
        <div className="bg-slate-900/50 border border-slate-800 p-3 rounded-lg relative overflow-hidden group hover:border-red-500/30 transition-colors">
           <div className="text-[10px] uppercase text-slate-500 font-bold tracking-wider mb-1">Debunked (1h)</div>
           <div className="text-2xl font-mono text-red-400 font-bold">{stats.debunked}</div>
           <i className="fas fa-shield-virus absolute -bottom-2 -right-2 text-4xl text-slate-800 group-hover:text-red-900 transition-colors"></i>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-slate-900/30 border border-slate-800 rounded-xl p-4 flex-grow flex flex-col min-h-[180px]">
        <h4 className="text-xs font-bold text-slate-400 uppercase mb-4 flex items-center justify-between">
           <span>Detection Velocity</span>
           <span className="text-[10px] bg-slate-800 px-2 py-1 rounded text-cyan-400">Live</span>
        </h4>
        <div className="flex-grow w-full h-full min-h-[120px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="time" hide />
              <YAxis hide domain={[0, 'auto']} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                itemStyle={{ color: '#cbd5e1' }}
              />
              <Line 
                type="monotone" 
                dataKey="threats" 
                stroke="#ef4444" 
                strokeWidth={2} 
                dot={false}
                activeDot={{ r: 4, fill: '#ef4444' }}
                animationDuration={1000}
              />
              <Line 
                type="monotone" 
                dataKey="verified" 
                stroke="#10b981" 
                strokeWidth={2} 
                dot={false}
                activeDot={{ r: 4, fill: '#10b981' }}
                animationDuration={1000}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Trending Threats */}
      <div className="space-y-2">
         <h4 className="text-[10px] font-bold text-slate-500 uppercase">Top Trending Threats</h4>
         <div className="space-y-2">
            <div className="flex items-center justify-between p-2 bg-slate-900/30 border border-slate-800/50 rounded hover:bg-slate-900/60 transition-colors cursor-pointer">
               <div className="flex items-center space-x-2 overflow-hidden">
                  <span className="text-red-500 text-xs">#1</span>
                  <p className="text-xs text-slate-300 truncate max-w-[150px]">"Dams opening at midnight..."</p>
               </div>
               <span className="text-[9px] bg-red-900/20 text-red-400 px-1.5 py-0.5 rounded border border-red-500/20">SCAM</span>
            </div>
            <div className="flex items-center justify-between p-2 bg-slate-900/30 border border-slate-800/50 rounded hover:bg-slate-900/60 transition-colors cursor-pointer">
               <div className="flex items-center space-x-2 overflow-hidden">
                  <span className="text-amber-500 text-xs">#2</span>
                  <p className="text-xs text-slate-300 truncate max-w-[150px]">"Free data for victims..."</p>
               </div>
               <span className="text-[9px] bg-amber-900/20 text-amber-400 px-1.5 py-0.5 rounded border border-amber-500/20">SUS</span>
            </div>
         </div>
      </div>

    </div>
  );
};

export default StatsPanel;
