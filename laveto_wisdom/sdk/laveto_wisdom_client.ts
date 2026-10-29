/**
 * Laveto Wisdom AW — TypeScript Enterprise Client SDK.
 * Compatible with Node.js 18+, Bun, and Deno.
 */

export interface AuditDossier {
  audit_id: string;
  posture: "HALT" | "CALIBRATE" | "RECALIBRATE" | "PROCEED";
  wisdom_quotient: number;
  formula: string;
  passes: {
    pass_1_intent: Record<string, any>;
    pass_2_causal: Record<string, any>;
    pass_3_axiological: Record<string, any>;
    pass_4_epistemic: {
      critical_blindspot: string;
      door_type: "ONE_WAY_DOOR" | "TWO_WAY_DOOR";
      downside_asymmetry: string;
    };
    pass_5_verdict: {
      calibrated_roadmap: string[];
      the_uncomfortable_truth: string;
    };
  };
}

export class LavetoClient {
  private apiKey: string;
  private endpoint: string;

  constructor(apiKey: string, endpoint: string = "https://p20.laveto.net/wisdom/api/v1/audit") {
    if (!apiKey) throw new Error("API key is required for LavetoClient");
    this.apiKey = apiKey;
    this.endpoint = endpoint;
  }

  public async auditProposal(proposal: string): Promise<AuditDossier> {
    const res = await fetch(this.endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Laveto-Key": this.apiKey,
        "User-Agent": "Laveto-SDK-TS/1.0"
      },
      body: JSON.stringify({ proposal })
    });

    if (res.status === 429) {
      throw new Error("Rate limit exceeded: 60 req/min threshold breached.");
    }
    if (res.status === 403) {
      throw new Error("Monthly audit quota exhausted for this credential.");
    }
    if (!res.ok) {
      throw new Error(`Laveto API returned HTTP ${res.status}: ${await res.text()}`);
    }

    return (await res.json()) as AuditDossier;
  }
}
