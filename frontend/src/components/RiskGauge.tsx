import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface RiskGaugeProps {
  score: number;
}

const RiskGauge: React.FC<RiskGaugeProps> = ({ score }) => {
  const data = [
    { name: 'Score', value: score },
    { name: 'Remaining', value: 100 - score },
  ];

  // Determine color based on score
  let color = '#10b981'; // Emerald (Safe)
  let colorName = 'Safe';
  if (score > 30) {
    color = '#f59e0b'; // Amber (Suspicious)
    colorName = 'Suspicious';
  }
  if (score > 70) {
    color = '#ef4444'; // Red (Scam)
    colorName = 'High Risk';
  }

  return (
    <div className="w-full flex flex-col items-center justify-center space-y-4 py-2">
      {/* Score Display Section - Top, completely separate */}
      <div className="flex flex-col items-center justify-center w-full">
        <div className="flex items-baseline justify-center gap-1 mb-1">
          <div 
            className="text-5xl font-black font-mono drop-shadow-lg leading-none" 
            style={{ color }}
          >
            {score}
          </div>
          <div className="text-xl font-bold font-mono text-slate-500">/100</div>
        </div>
        <div className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold mb-1">
          Risk Score
        </div>
        <div 
          className="text-sm uppercase tracking-wider font-bold"
          style={{ color }}
        >
          {colorName}
        </div>
      </div>
      
      {/* Gauge Arc Section - Middle, well separated */}
      <div className="relative w-full h-32 flex items-end justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="100%"
              startAngle={180}
              endAngle={0}
              innerRadius={35}
              outerRadius={55}
              paddingAngle={2}
              dataKey="value"
              stroke="none"
            >
              <Cell key="cell-0" fill={color} />
              <Cell key="cell-1" fill="#1e293b" /> 
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
      
      {/* Risk Level Indicators - Bottom, completely separate */}
      <div className="flex justify-between w-full px-6 text-[10px] text-slate-500 mt-2">
        <span className={score < 40 ? 'text-emerald-400 font-bold' : 'text-slate-500'}>Safe</span>
        <span className={score >= 40 && score < 70 ? 'text-amber-400 font-bold' : 'text-slate-500'}>Caution</span>
        <span className={score >= 70 ? 'text-red-400 font-bold' : 'text-slate-500'}>Danger</span>
      </div>
    </div>
  );
};

export default RiskGauge;
