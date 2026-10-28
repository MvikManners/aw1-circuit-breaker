'use strict';

/**
 * AW-1 Sovereign Runtime Guard: TypeScript / Node.js Circuit Breaker
 * Deterministic, sub-millisecond pre-execution safety gate for AI Agent tool calls.
 * Zero external dependencies.
 */

class ExecutionHalt extends Error {
  constructor(message, violationType, payloadSample) {
    super(`[AW1_CIRCUIT_BREAKER_HALT] ${message}`);
    this.name = 'ExecutionHalt';
    this.violationType = violationType;
    this.payloadSample = payloadSample ? payloadSample.slice(0, 120) : '';
    this.timestamp = new Date().toISOString();
  }
}

class ExecutionBreaker {
  constructor(options = {}) {
    this.strictMode = options.strictMode !== false;
    this.allowEnvReads = options.allowEnvReads || false;

    // Forbidden primitive definitions
    this.blockedTokens = [
      // Dangerous child processes & shells
      'child_process', 'execSync', 'spawnSync', 'execFile', 'fork',
      '/bin/sh', '/bin/bash', 'cmd.exe', 'powershell',
      
      // Dynamic code reflection
      'eval(', 'new Function', 'Function(', 'vm.runInContext', 'vm.runInThisContext',
      'process.binding', 'process.mainModule',
      
      // Network socket escapes
      'net.createConnection', 'net.connect', 'dgram.createSocket',
      
      // Credential & sensitive path exfiltration
      '.ssh/id_rsa', '.ssh/id_ed25519', '.ssh/authorized_keys',
      '/etc/passwd', '/etc/shadow', '.aws/credentials', '.env'
    ];

    // Regex patterns for obfuscated execution tunnels & base64 de-cloaking
    this.tunnelPatterns = [
      /Buffer\.from\s*\([^,]+,\s*['"]base64['"]\)/i,
      /atob\s*\(/i,
      /getattr\s*\(\s*__builtins__/i,
      /\bexec\s*\(\s*base64/i,
      /sh\s+-c\s+['"][^'"]*\b(curl|wget|nc|bash)\b/i,
      /rm\s+-rf\s+[/~]/i
    ];
  }

  /**
   * Evaluates input payload out-of-band and halts fail-closed on any violation.
   * @param {string|object} payload The raw tool call argument or script
   * @throws {ExecutionHalt} If an unsafe primitive or obfuscation tunnel is detected.
   */
  verifyOrHalt(payload) {
    const res = this.verify(payload);
    if (!res.allowed) {
      throw new ExecutionHalt(res.reason, res.violationType, res.payloadSample);
    }
    return true;
  }

  /**
   * Inspects payload and returns structured verification telemetry.
   * @param {string|object} payload
   * @returns {{ allowed: boolean, reason?: string, violationType?: string, latencyMs: number }}
   */
  verify(payload) {
    const start = (typeof performance !== 'undefined' && performance.now) 
      ? performance.now() 
      : Date.now();

    const text = typeof payload === 'string' ? payload : JSON.stringify(payload || {});
    
    // 1. Direct forbidden token check
    for (let i = 0; i < this.blockedTokens.length; i++) {
      const token = this.blockedTokens[i];
      if (text.includes(token)) {
        const latencyMs = this._calcLatency(start);
        return {
          allowed: false,
          reason: `Dangerous execution primitive detected: ${token}`,
          violationType: 'FORBIDDEN_PRIMITIVE',
          payloadSample: text,
          latencyMs
        };
      }
    }

    // 2. Obfuscation & Steganographic tunnel check
    for (let i = 0; i < this.tunnelPatterns.length; i++) {
      const pattern = this.tunnelPatterns[i];
      if (pattern.test(text)) {
        const latencyMs = this._calcLatency(start);
        return {
          allowed: false,
          reason: `Obfuscated execution tunnel pattern detected: ${pattern}`,
          violationType: 'STEGANOGRAPHIC_TUNNEL',
          payloadSample: text,
          latencyMs
        };
      }
    }

    // 3. Base64 unpacker simulation (catches de-obfuscated child_process / rm -rf)
    if (text.includes('base64') || text.includes('Buffer.from')) {
      try {
        const b64Match = text.match(/['"]([A-Za-z0-9+/=]{16,})['"]/);
        if (b64Match && b64Match[1]) {
          const decoded = Buffer.from(b64Match[1], 'base64').toString('utf8');
          for (let i = 0; i < this.blockedTokens.length; i++) {
            if (decoded.includes(this.blockedTokens[i])) {
              const latencyMs = this._calcLatency(start);
              return {
                allowed: false,
                reason: `De-cloaked Base64 payload contains forbidden token: ${this.blockedTokens[i]}`,
                violationType: 'DECLOAKED_TUNNEL',
                payloadSample: decoded,
                latencyMs
              };
            }
          }
        }
      } catch (e) {
        // Safe pass-through if not decodable
      }
    }

    const latencyMs = this._calcLatency(start);
    return {
      allowed: true,
      latencyMs
    };
  }

  _calcLatency(start) {
    const end = (typeof performance !== 'undefined' && performance.now) 
      ? performance.now() 
      : Date.now();
    return Math.max(0.001, parseFloat((end - start).toFixed(4)));
  }
}

module.exports = {
  ExecutionBreaker,
  ExecutionHalt
};
