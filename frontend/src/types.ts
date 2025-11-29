export enum Verdict {
  SAFE = 'SAFE',
  SUSPICIOUS = 'SUSPICIOUS',
  SCAM = 'SCAM'
}

export enum EntityType {
  PHONE = 'PHONE',
  EMAIL = 'EMAIL',
  URL = 'URL',
  ORGANIZATION = 'ORGANIZATION',
  CRYPTO_WALLET = 'CRYPTO_WALLET'
}

export interface Entity {
  type: EntityType;
  value: string;
  verificationStatus: string;
  isFlagged: boolean;
}

export interface VerificationResult {
  riskScore: number; // 0 to 100
  verdict: Verdict;
  summary: string;
  entities: Entity[];
  evidencePoints: string[];
  recommendation: string;
  sources: Array<{ title: string; uri: string }>;
}

export interface AnalysisState {
  status: 'idle' | 'analyzing' | 'complete' | 'error';
  progressStep: string;
  error?: string;
  result?: VerificationResult;
  imagePreview?: string;
}

