import React from 'react';
import { VerificationResult, Verdict, EntityType } from '../types';
import RiskGauge from './RiskGauge';
import WarningBlock, { WarningType } from './WarningBlock';

interface ReportDashboardProps {
  result: VerificationResult;
  onReset: () => void;
}

const ReportDashboard: React.FC<ReportDashboardProps> = ({ result, onReset }) => {
  const getVerdictColor = (verdict: Verdict) => {
    switch (verdict) {
      case Verdict.SAFE: return 'text-emerald-400 border-emerald-500/30 bg-emerald-950/20';
      case Verdict.SUSPICIOUS: return 'text-amber-400 border-amber-500/30 bg-amber-950/20';
      case Verdict.SCAM: return 'text-red-500 border-red-500/30 bg-red-950/20';
      default: return 'text-slate-400';
    }
  };

  const getEntityIcon = (type: EntityType) => {
    switch (type) {
      case EntityType.PHONE: return 'fa-phone';
      case EntityType.URL: return 'fa-link';
      case EntityType.EMAIL: return 'fa-envelope';
      case EntityType.CRYPTO_WALLET: return 'fa-wallet';
      default: return 'fa-building';
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-6 animate-fade-in-up pb-12">
      
      {/* Header Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Verdict Card */}
        <div className={`col-span-1 p-6 rounded-2xl border backdrop-blur-md flex flex-col items-center justify-center ${getVerdictColor(result.verdict)}`}>
          <h2 className="text-sm uppercase tracking-[0.2em] mb-2 opacity-80">Final Verdict</h2>
          <div className="text-4xl font-black tracking-tighter">{result.verdict}</div>
        </div>

        {/* Risk Gauge */}
        <div className="col-span-1 p-6 rounded-2xl bg-slate-900/50 border border-slate-800 backdrop-blur-md">
          <RiskGauge score={result.riskScore} />
        </div>

        {/* Summary Card */}
        <div className="col-span-1 p-6 rounded-2xl bg-slate-900/50 border border-slate-800 backdrop-blur-md flex flex-col justify-center">
            <h3 className="text-cyan-400 font-mono text-xs uppercase mb-3 flex items-center">
              <i className="fas fa-file-alt mr-2"></i>Executive Summary
            </h3>
            <div className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
                {result.summary.split('\n').map((paragraph, idx) => 
                  paragraph.trim() ? (
                    <p key={idx} className="mb-3 last:mb-0">
                      {paragraph.trim()}
                    </p>
                  ) : null
                )}
            </div>
        </div>
      </div>

      {/* Warning Blocks - Show only when relevant */}
      <div className="space-y-4">
        {/* CRITICAL WARNING - Only for SCAM verdict */}
        {result.verdict === Verdict.SCAM && (
          <WarningBlock
            type={WarningType.CRITICAL}
            title="🚨 CRITICAL WARNING - HIGH RISK DETECTED"
            message="This resource has been flagged as a potential SCAM. Do NOT proceed with any transactions or share personal information."
            details={[
              "Strong indicators of fraudulent activity detected",
              "Multiple risk factors identified",
              "Recommendation: Report to authorities if already engaged"
            ]}
          />
        )}
        
        {/* SUSPICIOUS WARNING - Only for SUSPICIOUS verdict, and only if there are actual risk factors */}
        {result.verdict === Verdict.SUSPICIOUS && result.evidencePoints && result.evidencePoints.length > 0 && (
          <WarningBlock
            type={WarningType.SUSPICIOUS}
            title="⚠️ SUSPICIOUS ACTIVITY DETECTED"
            message="This resource shows concerning indicators. Exercise extreme caution and verify through multiple independent sources."
            details={result.evidencePoints.slice(0, 3).map((point: string) => point.replace('⚠️ WARNING: ', ''))}
          />
        )}
        
        {/* EXTRACTION WARNING - Only show if no entities AND no data was extracted (not just empty entities) */}
        {result.entities.length === 0 && result.evidencePoints && result.evidencePoints.some((point: string) => 
          point.includes('Unable to extract') || point.includes('extract')
        ) && (
          <WarningBlock
            type={WarningType.EXTRACTION_WARNING}
            title="📸 EXTRACTION WARNING"
            message="No contact information could be extracted from this image. This may indicate:"
            details={[
              "Poor image quality or blurry text",
              "Missing or unclear contact information on the flyer",
              "Processing errors - manual verification required"
            ]}
          />
        )}
        
        {/* FLAGGED ENTITIES - Only show if there are actually flagged entities */}
        {result.entities && result.entities.some((e: any) => e.isFlagged) && (
          <WarningBlock
            type={WarningType.HIGH_RISK}
            title="🔴 FLAGGED ENTITIES DETECTED"
            message="Some extracted entities have been flagged in our verification databases:"
            details={result.entities
              .filter((e: any) => e.isFlagged)
              .map((e: any) => `${e.type}: ${e.value} - ${e.verificationStatus}`)
            }
          />
        )}
        
        {/* HIGH RISK SCORE - Only for high scores that aren't already SCAM */}
        {result.riskScore >= 70 && result.verdict !== Verdict.SCAM && result.verdict !== Verdict.SUSPICIOUS && (
          <WarningBlock
            type={WarningType.HIGH_RISK}
            title="⚠️ HIGH RISK SCORE"
            message={`Risk score of ${result.riskScore}/100 indicates significant concerns.`}
            details={[
              "Multiple verification checks failed",
              "Strong recommendation to avoid this resource",
              "Consider using official disaster relief channels instead"
            ]}
          />
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Evidence & Entities */}
        <div className="lg:col-span-2 space-y-6">
            
            {/* Entity Analysis */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 bg-slate-900/80 flex items-center">
                    <i className="fas fa-magnifying-glass-chart text-cyan-500 mr-3"></i>
                    <h3 className="font-bold text-slate-200">Entity Forensics</h3>
                </div>
                <div className="divide-y divide-slate-800/50">
                    {result.entities.length === 0 && (
                        <div className="p-6 text-slate-500 text-center italic">No identifiable entities extracted.</div>
                    )}
                    {result.entities.map((entity, idx) => (
                        <div key={idx} className="p-4 hover:bg-slate-800/30 transition-colors">
                            <div className="flex items-start justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400">
                                        <i className={`fas ${getEntityIcon(entity.type)}`}></i>
                                    </div>
                                    <div>
                                        <div className="text-sm font-mono text-slate-200 break-all">{entity.value}</div>
                                        <div className="text-xs text-slate-500 uppercase">{entity.type}</div>
                                    </div>
                                </div>
                                {entity.isFlagged && (
                                    <span className="px-2 py-1 rounded text-xs font-bold bg-red-500/10 text-red-500 border border-red-500/20">
                                        FLAGGED
                                    </span>
                                )}
                            </div>
                            <div className="mt-2 text-xs text-slate-400 pl-11 border-l-2 border-slate-700 ml-4">
                                {entity.verificationStatus}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Evidence Points */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 bg-slate-900/80 flex items-center">
                    <i className="fas fa-list-check text-cyan-500 mr-3"></i>
                    <h3 className="font-bold text-slate-200">Evidence Log</h3>
                </div>
                <ul className="p-4 space-y-3">
                    {result.evidencePoints.length === 0 ? (
                        <li className="text-slate-500 text-center italic">No evidence points available.</li>
                    ) : (
                        result.evidencePoints.map((point, idx) => (
                            <li key={idx} className="flex items-start space-x-3 text-sm text-slate-300">
                                <i className="fas fa-caret-right text-cyan-500 mt-1"></i>
                                <span>{point}</span>
                            </li>
                        ))
                    )}
                </ul>
            </div>
        </div>

        {/* Right Column: Recommendations & Sources */}
        <div className="space-y-6">
             {/* Recommendation */}
             <div className="bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-700 rounded-2xl p-6 shadow-lg shadow-black/40">
                <h3 className="text-cyan-400 font-mono text-xs uppercase mb-4 flex items-center">
                    <i className="fas fa-robot mr-2"></i> AI Recommendation
                </h3>
                <p className="text-slate-200 text-sm font-medium leading-relaxed">
                    {result.recommendation}
                </p>
            </div>

            {/* Sources */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 bg-slate-900/80">
                    <h3 className="font-bold text-slate-400 text-xs uppercase">Verification Sources</h3>
                </div>
                <div className="p-2">
                    {result.sources.length === 0 ? (
                         <div className="p-2 text-xs text-slate-600 text-center">No external sources linked.</div>
                    ) : (
                        result.sources.map((source, idx) => (
                            <a 
                                key={idx} 
                                href={source.uri} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="block p-3 rounded hover:bg-slate-800 transition-colors group"
                            >
                                <div className="text-xs text-cyan-400 truncate group-hover:underline">
                                    <i className="fas fa-external-link-alt mr-2 text-[10px]"></i>
                                    {source.title}
                                </div>
                                <div className="text-[10px] text-slate-600 truncate mt-1">{source.uri}</div>
                            </a>
                        ))
                    )}
                </div>
            </div>

             <button 
                onClick={onReset}
                className="w-full py-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-600 transition-all font-mono text-sm uppercase tracking-wider flex items-center justify-center space-x-2"
            >
                <i className="fas fa-redo"></i>
                <span>Verify Another Flyer</span>
            </button>
        </div>

      </div>
    </div>
  );
};

export default ReportDashboard;

