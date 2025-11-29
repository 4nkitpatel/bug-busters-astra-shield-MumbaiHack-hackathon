import React from 'react';

export enum WarningType {
  CRITICAL = 'critical',
  HIGH_RISK = 'high_risk',
  SUSPICIOUS = 'suspicious',
  INFO = 'info',
  EXTRACTION_WARNING = 'extraction_warning'
}

interface WarningBlockProps {
  type: WarningType;
  title: string;
  message: string;
  details?: string[];
}

const WarningBlock: React.FC<WarningBlockProps> = ({ type, title, message, details }) => {
  const getWarningStyles = () => {
    switch (type) {
      case WarningType.CRITICAL:
        return {
          container: 'bg-red-950/40 border-red-500/50 border-2',
          icon: 'fa-exclamation-triangle text-red-500',
          title: 'text-red-400',
          message: 'text-red-200',
          glow: 'shadow-[0_0_20px_rgba(239,68,68,0.5)]'
        };
      case WarningType.HIGH_RISK:
        return {
          container: 'bg-orange-950/40 border-orange-500/50 border-2',
          icon: 'fa-exclamation-circle text-orange-500',
          title: 'text-orange-400',
          message: 'text-orange-200',
          glow: 'shadow-[0_0_20px_rgba(249,115,22,0.5)]'
        };
      case WarningType.SUSPICIOUS:
        return {
          container: 'bg-amber-950/40 border-amber-500/50 border-2',
          icon: 'fa-question-circle text-amber-500',
          title: 'text-amber-400',
          message: 'text-amber-200',
          glow: 'shadow-[0_0_20px_rgba(245,158,11,0.5)]'
        };
      case WarningType.EXTRACTION_WARNING:
        return {
          container: 'bg-yellow-950/40 border-yellow-500/50 border-2',
          icon: 'fa-image text-yellow-500',
          title: 'text-yellow-400',
          message: 'text-yellow-200',
          glow: 'shadow-[0_0_20px_rgba(234,179,8,0.5)]'
        };
      case WarningType.INFO:
      default:
        return {
          container: 'bg-blue-950/40 border-blue-500/50 border-2',
          icon: 'fa-info-circle text-blue-500',
          title: 'text-blue-400',
          message: 'text-blue-200',
          glow: 'shadow-[0_0_20px_rgba(59,130,246,0.5)]'
        };
    }
  };

  const styles = getWarningStyles();

  return (
    <div className={`${styles.container} ${styles.glow} rounded-2xl p-6 mb-4 backdrop-blur-sm animate-fade-in`}>
      <div className="flex items-start space-x-4">
        <div className={`text-3xl ${styles.icon} flex-shrink-0`}>
          <i className={`fas ${styles.icon.split(' ')[1]}`}></i>
        </div>
        <div className="flex-1">
          <h3 className={`${styles.title} font-bold text-lg mb-2 flex items-center gap-2`}>
            {title}
          </h3>
          <p className={`${styles.message} text-sm leading-relaxed mb-3`}>
            {message}
          </p>
          {details && details.length > 0 && (
            <ul className={`${styles.message} text-sm space-y-1 ml-4 list-disc`}>
              {details.map((detail, idx) => (
                <li key={idx}>{detail}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default WarningBlock;

