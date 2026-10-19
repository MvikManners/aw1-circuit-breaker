# AW-1 Attestation Lifecycle & Key Management Specification

## 1. Zero-PII Consensus Boundary
To comply with global data privacy mandates and Bank of Botswana trust regulations, no customer identifiable information (PII), bank account numbers, or raw financial amounts are ever broadcast to Hedera Consensus Service (HCS). Only deterministic cryptographic digests (SHA-256) of signed deployment manifests and transaction audit dossiers are anchored.

## 2. Key Separation Model
The AW-1 governance pipeline strictly isolates operational network fees from cryptographic attestation authority:

1. **Operator Key (Hedera Submitter)**:
   - Signs HCS ConsensusSubmitMessage transactions.
   - Manages network transaction fee payments.
   - Rotated every 90 days via standard Hedera account key threshold updates.
2. **Release Signer Key (Manifest Signer)**:
   - Dedicated Ed25519 keypair (`AW1-RELEASE-ED25519-KEY-xx`).
   - Used exclusively to sign deployment manifests, build artifact hashes, and code release state.
   - Never touches transaction fee accounts.

## 3. Key Rotation & Revocation Protocol
- **Scheduled Rotation**: Release signing keys rotate on a 90-day cadence. When rotating from `KEY-N` to `KEY-(N+1)`, a `KEY_ROTATION_EVENT` manifest is anchored to HCS. The rotation payload contains the public key of `KEY-(N+1)` countersigned by `KEY-N`.
- **Emergency Revocation**: If a private signing key is suspected compromised, an immediate `KEY_REVOCATION` message is submitted with sequence priority, establishing an immutable consensus cutoff timestamp $T_{\text{revoke}}$. Any attestations stamped after $T_{\text{revoke}}$ signed by the compromised key are treated as void by automated audit verifiers.

## 4. Attestation Supersession DAG
When an erratum, security patch, or version bump occurs (e.g., v2.0.2 superseding v2.0.1):
1. The new deployment manifest includes backward hash pointers:
   - `supersedes_prior_anchor`: The Hedera topic sequence number of the prior deployment (e.g., `0.0.YOUR_TOPIC_ID:141391`).
   - `supersedes_manifest_hash`: The SHA-256 hash of the superseded manifest.
   - `amendment_reason`: Structured enum explaining the deployment trigger.
2. Auditors verify runtime provenance by traversing the backward hash pointer graph on-ledger, confirming unbroken operational succession.

## 5. Runtime Production Binding
Prior to accepting external gateway connections, the production WSGI supervisor verifies that:
$$\text{SHA256}(\text{ast\_breaker.py}_{\text{disk}}) == \text{Manifest}(\text{artifacts.ast\_breaker.sha256})$$
If file integrity deviates from the anchored manifest, the gateway enters `FAIL_CLOSED` mode and refuses all incoming tool calls.
