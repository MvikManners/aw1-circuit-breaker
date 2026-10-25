# AW-1 Provenance & Ledger Baseline Audit Record

- **Document Identifier:** AW1-NOTE-AUDIT-BASELINE-20261019
- **Point-in-Time Audit Snapshot Window:** 2026-10-19 19:35:00 UTC – 2026-10-19 20:45:00 UTC
- **Auditing Interface:** MCP Database Inspection Route (Claude Desktop External Probe)
- **Target Ledger:** Laveto Wisdom AW-1 Governor & MySQL Ledger (lavetolab.pythonanywhere.com)

---

## 1. Evidential Taxonomy

Findings are cataloged under three strict evidentiary standards:
1. **[Empirical - Verified]**: Directly observed, counted, or computed from raw database query outputs during the audit window.
2. **[Operational Attribution - Laveto Lab]**: Internal engineering classifications, environment rationales, or architectural intent asserted by Laveto Lab management that were not directly inspected at the infrastructure layer.
3. **[Regulatory Posture - Attestation]**: Legal and statutory positioning under Bank of Botswana (BoB) Electronic Payment Services (EPS) regulations, subject to external institutional confirmation.

---

## 2. Formal Findings

### Point 1: Active Audit Entries (#31–#43)
- **[Empirical - Verified]**: Exactly 13 rows exist in `ledger_entries` covering IDs #31 through #43 inclusive. All 13 rows possess non-empty `execution_token` strings (`AW1-REBALANCE-...` or `AW1-EXEC-TOKEN-...`) and non-empty 64-character hexadecimal `dossier_hash` values. All 13 transactions route through channel `INTERNAL_BOOK`.
- **[Empirical - Verified]**: The active schema contains no `parent_hash`, `prev_dossier_hash`, or `running_hash` columns in `ledger_entries` or `aw1_hcs_anchors`. Entries #31–#43 represent point-in-time hashed records; no cryptographic chaining or Merkle linkage between consecutive entries exists in the database schema.
- **[Empirical - Verified]**: Entry #31 transfers 325,000.00 BWP from source `BW-AUDIT-TEST` to `STATUTORY_RESERVE_VAULT` at 12:42:28 UTC. Entries #32 through #43 represent 12 disbursements from `STATUTORY_RESERVE_VAULT` to `BW-ACC-9921` totaling 36.50 BWP between 13:26:00 and 18:36:00 UTC.

### Point 2: Consensus Anchoring (`aw1_hcs_anchors`)
- **[Empirical - Verified]**: Exactly 13 records in `aw1_hcs_anchors` match the dossier hashes of entries #31–#43. All 13 display status `CONFIRMED` and `retry_count = 0`, written in three batches around 17:51, 18:22, and 19:12 UTC.
- **[Empirical - Verified]**: Every anchor record displays `topic_id = 0.0.YOUR_TOPIC_ID` and `hcs_tx_id` containing `YOUR_ACCOUNT_ID`. The recorded `hcs_sequence_number` values are non-monotonic (e.g., jumping from 292565 down to 141308). These values do not represent a production Hedera Consensus Service topic.
- **[Operational Attribution - Laveto Lab]**: Laveto Lab attributes these values to worker execution against an unpopulated local test configuration/mock harness (`hcs_config.json`). This root cause represents an engineering assertion and was not verified via server environment inspection during the audit.

### Point 3: Pre-Audit Staging & Quarantine (#1–#30)
- **[Empirical - Verified]**: `ledger_entries_quarantine` contains exactly 11 rows (IDs #16 through #26), totaling 130,000.00 nominal units (`amount_bwp`), all displaying source `STATUTORY_RESERVE_USD`, destination `US-PARTNER-NODE-09`, channel `CROSS_BORDER_ISO20022`, and timestamp `2026-10-19 13:05:01`.
- **[Empirical - Verified]**: `iso20022_audit_log` contains 0 message emissions for `entry_id BETWEEN 16 AND 26`. (Condition: Bounded strictly to the records in `iso20022_audit_log`).
- **[Empirical - Verified]**: In the accounts table, `STATUTORY_RESERVE_USD` ($15,800.00) and `US-PARTNER-NODE-09` ($2,200.00) both reflect `updated_at = 2026-10-19 03:34:55`, which predates the 13:05:01 quarantine event by approximately 9.5 hours. Zero balance mutation is confirmed for these two USD accounts; domestic BWP accounts were not inspected for quarantine-related variance.
- **[Empirical - Verified]**: Audit row #77 in `aw1_dossier_log` (`2026-10-19 13:05:01`) documents the quarantine action under `GATE_6_FIDUCIARY_REBALANCE` and token `AW1-QUARANTINE-DA52FE0C7C029CA5`. The raw payload cites `AW1-TREASURY-ED25519-MASTER` as cosigner; the log row contains no cryptographic signature payload.
- **[Empirical - Verified]**: Exactly 19 staging rows (IDs #1–#15 and #27–#30) remain in the live `ledger_entries` table:
  - **Unhashed Records (13 rows)**: Entries `#2, #3, #7, #10, #11, #12, #13, #14, #15, #27, #28, #29, #30`.
  - **Hashed Records (6 rows)**: Entries `#1, #4, #5, #6, #8, #9`.
- **[Operational Attribution - Laveto Lab]**: Laveto Lab designates these unhashed rows as pre-audit integration test records generated before Gate 0 dossier hash enforcement.

### Point 4: Fiduciary Reserve Capitalization (Entry #31)
- **[Empirical - Verified]**: The 325,000.00 BWP credit to `STATUTORY_RESERVE_VAULT` in Entry #31 originated from account `BW-AUDIT-TEST`, classified as `TEST_STAGING` by `v_accounts_normalized`.
- **[Regulatory Posture - Attestation]**: Laveto Lab documents this entry as a synthetic capitalization anchor intended to establish a pre-commissioning reserve buffer under Bank of Botswana EPS Section 14 guidelines. It does not represent a certified fiat escrow deposit held at a regulated commercial banking institution.

### Point 5: USD Silo Parity & Currency Normalization
- **[Empirical - Verified]**: As of the query snapshot at 2026-10-19 20:30 UTC, the complete USD silo consists of exactly three accounts:
  - `STATUTORY_RESERVE_USD`: $15,800.00 (`RESERVE_ESCROW`)
  - `US-CORP-SETTLE-01`: $2,000.00 (`CLIENT_LIABILITY` via heuristic)
  - `US-PARTNER-NODE-09`: $2,200.00 (`CLIENT_LIABILITY` via heuristic)
- **[Empirical - Scope Bounded]**: The classification of `US-CORP-SETTLE-01` and `US-PARTNER-NODE-09` as `CLIENT_LIABILITY` derives strictly from the fallback rule in `v_accounts_normalized` (all accounts not matching reserve identifiers or test prefixes default to client liability). It reflects a view-driven heuristic rather than an audited legal master service agreement or custodial contract.
- **[Empirical - Verified]**: Under this heuristic classification, total USD client liabilities are $4,200.00 against $15,800.00 in escrow, establishing an audited point-in-time reserve backing ratio of **376.19%**.
- **[Empirical - Verified]**: `v_accounts_normalized` defines `domestic_bwp_balance` as `balance_bwp` when `currency = 'BWP'` and `NULL` for all other currencies. It performs no foreign exchange spot rate conversion or multi-currency consolidation.
- **[Empirical - Verified]**: The column `accounts.balance_bwp` holds nominal native values ($15,800.00 USD, $2,000.00 USD, $2,200.00 USD) rather than converted BWP values.
- **[Regulatory Posture - Attestation]**: Laveto Lab maintains that the `NULL` domestic BWP balance reflects mandatory statutory segregation between domestic Pula liabilities and cross-border foreign exchange holdings under BoB EPS Section 14.
