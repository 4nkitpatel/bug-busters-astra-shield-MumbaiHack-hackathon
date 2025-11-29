
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
  sources: Array<{ title: string; uri: string; confidence?: number; status?: 'verified' | 'refuted' | 'inconclusive' }>;
}

export interface AnalysisState {
  status: 'idle' | 'analyzing' | 'complete' | 'error';
  progressStep: string;
  error?: string;
  result?: VerificationResult;
  imagePreview?: string;
}

// Monitoring Feed Types
export type ClaimStatus = 'DETECTING' | 'VERIFYING' | 'VERIFIED' | 'DEBUNKED';
export type ClaimSource = 'Twitter' | 'Facebook' | 'WhatsApp' | string;

export interface Claim {
  id: string;
  text: string;
  source: ClaimSource;
  timestamp: string; // ISO or relative string
  engagementSpike: string;
  status: ClaimStatus;
  riskScore?: number;
  verdict?: Verdict;
  isUserSubmission?: boolean;
  url?: string;
}
