# INSTITUTIONAL REGULATORY COMPLIANCE CIRCULAR
**Reference:** LVT-REG-CIRC-2026-001  
**Jurisdiction:** Republic of Botswana  
**Supervisory Oversight:** Bank of Botswana (National Payment System) | CEE Act 2021 Statutory Mandate  
**Target Audience:** Dikgosi, Ward Heads, Village Treasurers, Society Administrators, and Registered Merchants  
**Effective Date:** 1 October 2026  

---

## 1. ENGLISH VERSION

### Purpose & Statutory Framework
This circular serves as official notice to all participating village leadership, cooperative society executives, and merchants that **Laveto Pay** and the **AW-1 Circuit Breaker** have operationalized automated statutory compliance controls across all disbursement, off-ramp, and liquidity advance rails.

### Core Compliance Protocols
1. **Bank of Botswana 1-to-1 Trust Backing (National Payment System Act)**:
   - 100% of digital ledger balances and active token liabilities are backed on a 1-to-1 basis by liquid BWP reserves in designated statutory escrow accounts.
   - Reconciliation occurs nightly at 23:55 CAT. Any float deficit automatically halts non-essential outbound rails.
2. **Citizen Economic Empowerment (CEE Act 2021 / CEDA) Gating**:
   - Outbound disbursements, claims, and liquidity advances are evaluated against statutory citizen equity quotas ($\ge 50\%$).
   - Any transaction falling below statutory thresholds is intercepted before transmission with an immutable execution block (`HTTP 422 HALT`).
3. **Cryptographic Ledger Integrity & Independent Auditability**:
   - Every clearance or halt produces a unique SHA-256 statutory seal.
   - Any authorized officer, auditor, or village administrator may independently verify a seal's authenticity at:
     ```
     [https://p20.laveto.net/wisdom/api/v1/compliance/verify/](https://p20.laveto.net/wisdom/api/v1/compliance/verify/)<seal_hash>
     ```

---

## 2. TEME YA SETSWANA

### Maikaelelo le Melao ya Puso
Kitsiso e e rebotswe semmuso go ya go Dikgosi, Dikgosana, Matlotlo a Makgotla a Metse le Baemedi ba Dikgwebo go ba itsise fa **Laveto Pay** mmogo le lenaneo la tshireletso la **AW-1 Circuit Breaker** a tsentse tirisong melawana e e gagametseng ya tsa melao ya dituelo, ditumalano tsa polokelo le go ntshiwa ga madi a ditirelo tsa leotwana.

### Dintlha tsa Konokono tsa Tsetlana e ya Melao
1. **Polokelo ya Madi go ya ka Melawana ya Banka ya Botswana (1-to-1 Trust Parity)**:
   - Pula nngwe le nngwe e e mo lenaneong la kgwebo e patilwe ke madi a mmatota (100% liquid fiat reserves) a a bolokilweng mo polokelong e e sireletsegileng ya banka.
   - Tlhatlhobo ya dipalo e dirwa bosigo bongwe le bongwe ka nako ya 23:55 CAT go netefatsa gore ga gona madi ape a a dirisiwang ntle le thotloetso e e tletseng.
2. **Tsetlana ya Ditshwanelo tsa Batswana (CEE Act 2021 le CEDA)**:
   - Madi ape a dituelo le dithuso tsa potlako tsa metse a tlhatlhowa ke lenaneo go netefatsa gore seabe sa Batswana ga se wele tlase ga masome a matlhano mo lekgolong ($50\%$).
   - Fa tsetlana e e ka tlolwa, lenaneo le itsa madi go fetela pele koo le koo ka khunololo ya motlakase ya `HTTP 422 HALT`.
3. **Bopaki jo bo Kgethegileng jwa Pabalelo (SHA-256 Cryptographic Seal)**:
   - Tiragalo nngwe le nngwe e e letleletsweng kgotsa e e thibetsweng e tlamelwa ka nomoro ya bopaki e e ka se kang ya fetolwa ke ope.
   - Moeteledipele, mothatlobi wa dibuka kgotsa kgosi a ka sekaseka bopaki jo ka go tsena mo atereseng e:
     ```
     [https://p20.laveto.net/wisdom/api/v1/compliance/verify/](https://p20.laveto.net/wisdom/api/v1/compliance/verify/)<seal_hash>
     ```

---
**Ofisi ya Taolo le Ditumalanano (Laveto Compliance & Governance Unit)**  
Gaborone, Republic of Botswana  
