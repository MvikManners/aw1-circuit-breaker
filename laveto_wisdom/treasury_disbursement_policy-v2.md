# 🏛️ LAVETO PTY LTD — AUTOMATED TREASURY DISBURSEMENT & POUC OFF-RAMP POLICY (V2)

**Document Control ID:** `LVT-POL-400-TREASURY-V2`  
**Classification:** Restricted / Commercial & Legal Standard  
**Supercedes:** `LVT-POL-400-TREASURY (v1)`  
**Effective Date:** October 8, 2026 | Gaborone, Republic of Botswana  
**Target Entities:** Laveto Sovereign Treasury, Commercial Operating Partners, Telco Clearing Aggregators (Orange Money, Mascom MyZaka, BTC Smega)  
**System Scope:** Laveto Pay (`/pay`), P20 Sovereign Ledger (`p20.laveto.net`), Wisdom AW-1 (`/wisdom`), PoUC Citizen Edge Network  

---

## SECTION 1: EXECUTIVE GOVERNANCE & THE SOVEREIGN ZERO-DRAIN ARCHITECTURE

### 1.1 Policy Mandate & Background
This policy governs the automated calculation, settlement, liquidity reserves, and disbursement of commercial partner commissions, merchant payments, and Proof of Useful Contribution (PoUC) citizen node off-ramp redemptions.

All treasury operations are bound to the **Zero Corporate Drain Rule**: Laveto Pty Ltd incurs zero out-of-pocket fiat expenditure for payouts. All disbursements, token redemptions, and partner commissions are funded strictly from newly generated, fully settled transaction spreads, enterprise audit retainers, and specialized protocol exit tolls.

### 1.2 The Economic Justification for the 10%–15% PoUC Off-Ramp Toll
1. **Zero Citizen Capital Outlay:** Citizen edge node operators invest zero financial capital; tokens are earned passively in the background while devices charge overnight on Wi-Fi during idle hours under strict thermal (≤ 34°C) and battery (≥ 80%) interlocks.
2. **100% Pure Profit to Nodes:** Every Pula received upon cash-out represents pure, unearned household profit. A 10% to 15% exit toll leaves the citizen with 85%–90% net cash yield while transforming the off-ramp into a self-funding sovereign clearinghouse.
3. **Internal Velocity Incentive (The Gravity Well):** While cashing out to mobile money incurs a 10%–15% toll, spending AWT inside the domestic economy via Laveto Pay carries a 0.0% fee. This incentivizes citizens to keep value circulating domestically for food, transport, and utilities rather than bleeding fiat reserves into external telco networks.
4. **Anti-Sybil & Bot Farm Annihilation:** High exit tolls make speculative bot-farming, headless Android emulators, and mercenary cloud scripts economically unviable, ensuring treasury liquidity is reserved exclusively for genuine human participants across Botswana.

---

## SECTION 2: PILLAR-BY-PILLAR RECONCILIATION & DISBURSEMENT MATRIX

| Pillar / Vertical | Revenue Origin & Basis | Exit Fee / Take-Rate | Settlement Rail | Frequency | Webhook Trigger Event |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Pillar 1: Laveto Pay (`/pay`)** | Merchant social commerce GMV | 2.0% Gross (1.2% telco cost, 0.8% net spread) | Orange Money / MyZaka / BWP EFT | Weekly (Mondays 08:00 CAT) | `PAYMENT_SETTLED_BATCH_CLOSED` |
| **Pillar 2: P20 Village Ledger** | Marketplace & Kgotla event tolls | 20% Net Tolls + 20% B2B Referrals | BWP Mobile Money / EFT | Bi-Weekly (1st & 15th) | `P20_VENDOR_COMMISSION_MINTED` |
| **Pillar 3: Wisdom AW-1 B2B** | CEDA, SEZA, PPRA, Bank Audit Retainers | 15% ACV Origination Commission | Bank EFT (Host-to-Host) | Monthly (30-day term) | `ENTERPRISE_RETAINER_CLEARED` |
| **Pillar 3.1: PoUC Citizen Off-Ramp** | Node AWT to BWP Mobile Money Cash-Out | **10.0% – 15.0% Tiered Exit Toll** | Orange Money / Mascom MyZaka | Real-Time (On Demand) | `POUC_NODE_OFFRAMP_COMPLETE` |
| **Pillar 3.2: Laveto Pay In-Store Spend** | Direct merchant purchases with AWT | **0.0% (Zero Fee Internal Spend)** | Local Laveto Pay QR / NFC | Instantaneous | `INTERNAL_AWT_COMMERCE_SETTLED` |
| **Pillar 4: System Restoration / Hangar** | CTO Govt Fleet & Diagnostic Kits | 10% Sourcing Margin Cut | Corporate EFT | Monthly | `BULK_KIT_DISPATCH_CONFIRMED` |

---

## SECTION 3: POUC OFF-RAMP TIERED FEE SCHEDULE & WATERFALL ALLOCATION

### 3.1 Tiered Exit Toll Schedule
| Cash-Out Bracket (BWP) | Gross Exit Toll | Effective Citizen Net Yield | Strategic Operational Purpose |
| :--- | :---: | :---: | :--- |
| **Tier 3: Micro Cash-Outs (< P250.00)** | **15.0%** | **85.0%** | Deters frequent sub-P50 requests; covers carrier costs. |
| **Tier 2: Standard Cash-Outs (P250.00 – P1,000.00)** | **12.5%** | **87.5%** | Standard weekly/monthly household liquidation rate. |
| **Tier 1: Bulk Guild Nodes (> P1,000.00)** | **10.0%** | **90.0%** | Preferred rate for high-reputation university builder nodes. |
| **Internal Spend: Laveto Pay Merchants** | **0.0% (Free)** | **100.0%** | Eliminates exit friction for purchasing groceries and utilities. |

---

## SECTION 4: THE NET TOLL WATERFALL FORMULA
1. **50% → Bank of Botswana (BoB) 1-to-1 Treasury Reserve Vault:** Permanently reinforces the liquid BWP cash escrow backing circulating AWT tokens.
2. **30% → Automated Open-Market Buyback-and-Burn Sink:** Purchases circulating AWT from the market and permanently destroys it.
3. **20% → Laveto Operating Surplus & Partner Commission Pool:** Compensates commercial operations, gateway infrastructure maintenance, and node cluster management.
