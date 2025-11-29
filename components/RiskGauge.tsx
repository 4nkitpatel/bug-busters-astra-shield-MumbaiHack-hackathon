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
  if (score > 30) color = '#f59e0b'; // Amber (Suspicious)
  if (score > 70) color = '#ef4444'; // Red (Scam)

  return (
    <div className="relative h-64 w-full flex flex-col items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="80%" 
            startAngle={180}
            endAngle={0}
            innerRadius={85} 
            outerRadius={110} 
            paddingAngle={0}
            dataKey="value"
            stroke="none"
          >
            <Cell key="cell-0" fill={color} />
            <Cell key="cell-1" fill="#1e293b" /> 
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      
      <div className="absolute top-[75%] left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center -mt-6">
        <div className="text-5xl font-bold font-mono tracking-tighter" style={{ color }}>{score}</div>
        <div className="text-xs text-slate-500 uppercase tracking-widest font-bold">Risk Score / 100</div>
      </div>
    </div>
  );
};

export default RiskGauge;