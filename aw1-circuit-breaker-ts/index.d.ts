export interface BreakerOptions {
  strictMode?: boolean;
  allowEnvReads?: boolean;
}

export interface VerificationResult {
  allowed: boolean;
  reason?: string;
  violationType?: string;
  payloadSample?: string;
  latencyMs: number;
}

export declare class ExecutionHalt extends Error {
  readonly violationType: string;
  readonly payloadSample: string;
  readonly timestamp: string;
  constructor(message: string, violationType?: string, payloadSample?: string);
}

export declare class ExecutionBreaker {
  constructor(options?: BreakerOptions);
  verifyOrHalt(payload: string | object): boolean;
  verify(payload: string | object): VerificationResult;
}
