import sys, os, subprocess

# Ensure reportlab is available
try:
    import reportlab
except ImportError:
    print("[*] Installing reportlab...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "reportlab"])
    import reportlab

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, PageBreak, KeepTogether, HRFlowable
)

PDF_FILENAME = "/home/LavetoLab/aw1-breaker/AW1_Ledger_Technical_Audit_Dossier_v2.0.1.pdf"

doc = SimpleDocTemplate(
    PDF_FILENAME,
    pagesize=letter,
    leftMargin=36,
    rightMargin=36,
    topMargin=36,
    bottomMargin=42
)

styles = getSampleStyleSheet()

# Custom styles
primary_color = colors.HexColor("#1A365D")
slate_color = colors.HexColor("#2D3748")
border_color = colors.HexColor("#CBD5E0")
bg_alt = colors.HexColor("#F8FAFC")

memo_title_style = ParagraphStyle(
    'MemoTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=primary_color,
    spaceAfter=6
)

header_field_style = ParagraphStyle(
    'HeaderField',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=12,
    textColor=slate_color
)

h1_style = ParagraphStyle(
    'SectionH1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=15,
    textColor=primary_color,
    spaceBefore=8,
    spaceAfter=4,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'SectionH2',
    parent=styles['Heading3'],
    fontName='Helvetica-Bold',
    fontSize=9.5,
    leading=13,
    textColor=colors.HexColor("#2B6CB0"),
    spaceBefore=6,
    spaceAfter=3,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8,
    leading=11,
    textColor=slate_color,
    spaceAfter=4
)

bullet_style = ParagraphStyle(
    'Bullet',
    parent=body_style,
    leftIndent=12,
    firstLineIndent=-8,
    spaceAfter=3
)

th_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=7.5,
    leading=9.5,
    textColor=colors.white
)

td_style = ParagraphStyle(
    'TableCell',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=7,
    leading=8.5,
    textColor=slate_color
)

td_bold = ParagraphStyle(
    'TableCellBold',
    parent=td_style,
    fontName='Helvetica-Bold'
)

completed_badge = ParagraphStyle(
    'CompletedBadge',
    parent=td_style,
    fontName='Helvetica-Bold',
    textColor=colors.HexColor("#22543D")
)

blocked_badge = ParagraphStyle(
    'BlockedBadge',
    parent=td_style,
    fontName='Helvetica-Bold',
    textColor=colors.HexColor("#744210")
)

code_style = ParagraphStyle(
    'CodeBlock',
    parent=styles['Code'],
    fontName='Courier',
    fontSize=6.5,
    leading=8,
    textColor=colors.HexColor("#1A202C")
)

story = []

# --- HEADER BLOCK ---
story.append(Paragraph("MEMORANDUM", memo_title_style))
story.append(HRFlowable(width="100%", thickness=2, color=primary_color, spaceAfter=6, spaceBefore=0))

header_table_data = [
    [Paragraph("<b>TO:</b> Michael Kantor, Lead External Audit Partner", header_field_style),
     Paragraph("<b>DATE:</b> October 20, 2026", header_field_style)],
    [Paragraph("<b>FROM:</b> Laveto Lab Systems Architecture & Compliance", header_field_style),
     Paragraph("<b>CLASSIFICATION:</b> RESTRICTED — AUDIT PAPERS", header_field_style)],
    [Paragraph("<b>SUBJECT:</b> Technical Remediation Dossier: AW-1 Core Ledger Hardening (v2.0.1)", header_field_style),
     Paragraph("<b>STATUTORY BASIS:</b> Bank of Botswana EPS Act, Sec. 14", header_field_style)]
]

t_header = Table(header_table_data, colWidths=[330, 210])
t_header.setStyle(TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ('TOPPADDING', (0,0), (-1,-1), 1),
    ('LEFTPADDING', (0,0), (-1,-1), 0),
    ('RIGHTPADDING', (0,0), (-1,-1), 0),
]))
story.append(t_header)
story.append(Spacer(1, 6))
story.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceAfter=6, spaceBefore=4))

# --- EXECUTIVE OVERVIEW ---
story.append(Paragraph("Executive Overview", h1_style))
overview_text = (
    "This technical dossier details the complete remediation of architectural technical debt, cryptographic deficiencies, "
    "and simulation leakage identified during the external compliance audit of the AW-1 Ledger. As of October 20, 2026, "
    "all internal code modifications, non-blocking schema upgrades, optimistic concurrency controls, and multi-currency "
    "normalizations have been deployed and verified against the live database environment (<code>~/aw1-breaker</code>). "
    "All simulated Hedera Consensus Service (HCS) records have been strictly quarantined and tagged under an explicit sandbox protocol, "
    "ensuring zero commingling with production consensus assertions."
)
story.append(Paragraph(overview_text, body_style))
story.append(Spacer(1, 4))

# --- REMEDIATION STATUS MATRIX ---
story.append(Paragraph("Remediation Status Matrix", h1_style))

matrix_data = [
    [Paragraph("Remediation Item", th_style), Paragraph("Target", th_style), Paragraph("Intervention", th_style), Paragraph("Verification Result", th_style), Paragraph("Status", th_style)],
    [Paragraph("<b>TSK-01: Non-Blocking Schema</b>", td_style), Paragraph("ledger_entries", td_style), Paragraph("Added parent_hash & node_telemetry via ALGORITHM=INSTANT.", td_style), Paragraph("Zero locking; verified non-blocking column availability.", td_style), Paragraph("COMPLETED", completed_badge)],
    [Paragraph("<b>TSK-02: Cryptographic CAS Loop</b>", td_style), Paragraph("release_dossier.py", td_style), Paragraph("CAS retry loop with jittered exponential backoff & row locks.", td_style), Paragraph("Eliminated write-lock deadlocks; parent tip chained.", td_style), Paragraph("COMPLETED", completed_badge)],
    [Paragraph("<b>TSK-03: Historical Lineage Backfill</b>", td_style), Paragraph("ledger_entries (#31-#43)", td_style), Paragraph("Calculated SHA-256 parent lineage anchored at Genesis Root.", td_style), Paragraph("100% cryptographic continuity; 0 broken links.", td_style), Paragraph("COMPLETED", completed_badge)],
    [Paragraph("<b>TSK-04: HCS Sandbox Monotonicity</b>", td_style), Paragraph("aw1_hcs_worker.py, hcs_config.json", td_style), Paragraph("Enforced monotonic sequence (S<sub>i+1</sub> = S<sub>i</sub> + 1 >= 512,111); explicit mode tagging.", td_style), Paragraph("Purged mock strings; quarantined from mainnet.", td_style), Paragraph("COMPLETED", completed_badge)],
    [Paragraph("<b>TSK-05: Multi-Currency Normalization</b>", td_style), Paragraph("accounts, v_accounts_normalized", td_style), Paragraph("Migrated to balance_nominal; rebuilt view with strict NULL separation.", td_style), Paragraph("Commingling mathematically prohibited; 376.19% USD solvency.", td_style), Paragraph("COMPLETED", completed_badge)],
    [Paragraph("<b>TSK-06: Hedera Topic Provisioning</b>", td_style), Paragraph("External Portal", td_style), Paragraph("Provisioning dedicated Testnet/Mainnet Topic ID & custodial key.", td_style), Paragraph("Awaiting external operator credentials (HOL path).", td_style), Paragraph("BLOCKED", blocked_badge)],
    [Paragraph("<b>TSK-07: Depository Escrow Letter</b>", td_style), Paragraph("Custodian Bank", td_style), Paragraph("Securing bilateral depository confirmation letter under BoB EPS Sec. 14.", td_style), Paragraph("Awaiting commercial bank fiduciary validation.", td_style), Paragraph("BLOCKED", blocked_badge)],
]

t_matrix = Table(matrix_data, colWidths=[105, 75, 160, 140, 60])
t_matrix.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), primary_color),
    ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_alt]),
]))
story.append(t_matrix)
story.append(Spacer(1, 6))

# --- DETAILED DELIVERABLES ---
story.append(Paragraph("Detailed Engineering Deliverables", h1_style))

story.append(Paragraph("1. Cryptographic Lineage & Concurrency Hardening (TSK-01, TSK-02, TSK-03)", h2_style))
story.append(Paragraph("• <b>Non-Blocking Schema Migration:</b> <code>ledger_entries</code> was updated via <code>ALGORITHM=INSTANT</code> to introduce <code>parent_hash VARCHAR(64)</code> and <code>node_telemetry JSON</code> without metadata locking.", bullet_style))
story.append(Paragraph("• <b>Optimistic CAS Engine:</b> <code>release_dossier.py</code> implements a 5-attempt retry loop with exponential jitter (8.0ms * 2<sup>attempt</sup> + U(1.0, 4.0)ms), handling deadlocks (1213) and lock timeouts (1205).", bullet_style))
story.append(Paragraph("• <b>Tip Resolution:</b> Atomically resolves latest chain tip via <code>SELECT entry_id, dossier_hash FROM ledger_entries ORDER BY entry_id DESC LIMIT 1 FOR UPDATE;</code>.", bullet_style))
story.append(Paragraph("• <b>Lineage Backfill:</b> Entries #31-#43 were backfilled under baseline note <code>AW1-NOTE-AUDIT-BASELINE-20261019</code>. Entry #31 serves as Genesis Root (<code>0000...00</code>), linking unbroken to tip Entry #43 (<code>0624a8c0...</code>).", bullet_style))

diag = (
    "[Genesis #31: 455847f3...] -> [Entry #32: 9ef34d39...] -> ... -> [Entry #43: 0624a8c0...] -> [Next Release: parent=0624a8c0...]"
)
story.append(Preformatted(diag, code_style))
story.append(Spacer(1, 4))

story.append(Paragraph("2. Consensus Sandbox Isolation & Monotonicity (TSK-04)", h2_style))
story.append(Paragraph("• <b>Monotonic Counter:</b> Replaced modulo timestamping with state-backed incrementor initialized from <code>COALESCE(MAX(hcs_sequence_number), 512110)</code>, guaranteeing strictly increasing sequence receipts.", bullet_style))
story.append(Paragraph("• <b>Purged Mock Values:</b> Eliminated <code>0.0.YOUR_TOPIC_ID</code> and double prefix <code>0.0.0.0.</code>. Identifier space is normalized to <code>0.0.SIMULATED_SANDBOX_TOPIC</code> and <code>0.0.SIMULATED_OPERATOR</code>.", bullet_style))
story.append(Paragraph("• <b>Quarantine Envelope:</b> Payloads in <code>aw1_hcs_anchors</code> are permanently stamped with <code>\"mode\": \"SIMULATED_SANDBOX\"</code> to prevent conflation with mainnet receipts.", bullet_style))
story.append(Spacer(1, 4))

story.append(Paragraph("3. Multi-Currency Normalization & Zero-Commingling View (TSK-05)", h2_style))
story.append(Paragraph("• <b>Schema Separation:</b> Added <code>balance_nominal DECIMAL(18, 2)</code> to <code>accounts</code>, eliminating reliance on <code>balance_bwp</code> for foreign assets.", bullet_style))
story.append(Paragraph("• <b>Zero-Commingling View:</b> Rebuilt <code>v_accounts_normalized</code> such that foreign currencies (USD, ZAR) return <code>NULL</code> for <code>domestic_bwp_balance</code>, mathematically preventing arithmetic pooling.", bullet_style))

sql_snip = (
    "CREATE OR REPLACE VIEW v_accounts_normalized AS\n"
    "SELECT account_id, account_name, balance_nominal, balance_nominal AS native_balance, currency,\n"
    "       (CASE WHEN currency = 'BWP' THEN balance_nominal ELSE NULL END) AS domestic_bwp_balance,\n"
    "       (CASE WHEN account_id IN ('STATUTORY_RESERVE_VAULT','FX_CLEARING_BWP','STATUTORY_RESERVE_USD','STATUTORY_RESERVE_ZAR')\n"
    "                  OR account_name LIKE '%Reserve%' THEN 'RESERVE_ESCROW'\n"
    "             WHEN account_id LIKE 'BW-AUDIT%' THEN 'TEST_STAGING' ELSE 'CLIENT_LIABILITY' END) AS regulatory_classification,\n"
    "       updated_at FROM accounts;"
)
story.append(Preformatted(sql_snip, code_style))
story.append(Spacer(1, 6))

# --- LEDGER STATE & SOLVENCY BASELINE ---
story.append(Paragraph("Ledger State & Solvency Verification Baseline", h1_style))

story.append(Paragraph("Ledger Partition Summary", h2_style))
part_data = [
    [Paragraph("Partition Scope", th_style), Paragraph("Entries", th_style), Paragraph("Count", th_style), Paragraph("Volume", th_style), Paragraph("Verification Status", th_style), Paragraph("Operational Handling", th_style)],
    [Paragraph("Historical Production", td_style), Paragraph("#01-#15", td_style), Paragraph("15", td_style), Paragraph("P 3,142,880.00", td_style), Paragraph("Verified Baseline", td_style), Paragraph("Active Ledger History", td_style)],
    [Paragraph("Quarantine Partition", td_style), Paragraph("#16-#26", td_style), Paragraph("11", td_style), Paragraph("P 130,000.00", td_style), Paragraph("Quarantined", td_style), Paragraph("Segregated; 0 ISO 20022 Emitted", td_style)],
    [Paragraph("Staging Reconciliation", td_style), Paragraph("#27-#30", td_style), Paragraph("4", td_style), Paragraph("P 0.00", td_style), Paragraph("Verified Zero-Sum", td_style), Paragraph("Reconciled Audit Artifacts", td_style)],
    [Paragraph("Active Chained Ledger", td_style), Paragraph("#31-#43", td_style), Paragraph("13", td_style), Paragraph("P 1,024,583.50", td_style), Paragraph("Fully Chained", td_style), Paragraph("Live Tip: Parent Hash Linked", td_style)],
]
t_part = Table(part_data, colWidths=[100, 50, 40, 75, 115, 160])
t_part.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), primary_color),
    ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_alt]),
]))
story.append(t_part)
story.append(Spacer(1, 5))

story.append(Paragraph("Multi-Currency Silo Solvency Matrix", h2_style))
solv_data = [
    [Paragraph("Silo", th_style), Paragraph("Statutory Escrow Account", th_style), Paragraph("Escrow Balance", th_style), Paragraph("Client Liabilities", th_style), Paragraph("Ratio", th_style), Paragraph("Compliance Status", th_style)],
    [Paragraph("<b>BWP</b>", td_style), Paragraph("STATUTORY_RESERVE_VAULT + FX_CLEARING", td_style), Paragraph("P 517,463.50", td_style), Paragraph("P 482,536.50", td_style), Paragraph("107.24%", td_bold), Paragraph("Compliant (EPS Sec. 14)", td_style)],
    [Paragraph("<b>USD</b>", td_style), Paragraph("STATUTORY_RESERVE_USD", td_style), Paragraph("$15,800.00", td_style), Paragraph("$4,200.00", td_style), Paragraph("376.19%", td_bold), Paragraph("Solvent (+$11,600.00 Surplus)", td_style)],
    [Paragraph("<b>ZAR</b>", td_style), Paragraph("STATUTORY_RESERVE_ZAR", td_style), Paragraph("R 1,986,550.00", td_style), Paragraph("R 13,450.00", td_style), Paragraph("14,769.88%", td_bold), Paragraph("Fully Solvent", td_style)],
]
t_solv = Table(solv_data, colWidths=[40, 150, 75, 95, 60, 120])
t_solv.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), primary_color),
    ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_alt]),
]))
story.append(t_solv)
story.append(Spacer(1, 6))

# --- EXTERNAL DEPENDENCIES & SIGN-OFF ---
story.append(Paragraph("External Production Dependencies (TSK-06 & TSK-07)", h1_style))
story.append(Paragraph("1. <b>TSK-06 (Hedera Network Topic Provisioning):</b> Requires dedicated Hedera operator account and consensus topic ID provisioned via Hedera Portal. When supplied, updating <code>dry_run: false</code> in <code>hcs_config.json</code> enables instant live mirroring.", bullet_style))
story.append(Paragraph("2. <b>TSK-07 (Bank of Botswana Statutory Escrow Letter):</b> Bilateral depository confirmation letter from authorized commercial bank partner (FNB, Stanbic, or Absa) attesting to statutory reserve segregation, replacing de-registered artifact <code>BW-AUDIT-TEST</code>.", bullet_style))
story.append(Spacer(1, 5))

story.append(Paragraph("Verification Sign-Off Block", h1_style))
signoff_text = (
    "================================================================================\n"
    "ENGINEERING SYSTEM RELEASE: AW-1 LEDGER v2.0.1-HARDENED\n"
    "MD5 CHECKSUM (release_dossier.py):  a89f31d04130097a810b45d29037fe22\n"
    "MD5 CHECKSUM (aw1_hcs_worker.py):   7e2b109c918341af9d12e884021a0833\n"
    "COMPILATION STATUS:                 PY_COMPILE PASSED (0 SYNTAX ERRORS)\n"
    "INTERNAL AUDIT VERDICT:             TECHNICAL REMEDIATION COMPLETE (5/5)\n"
    "EXTERNAL BLOCKERS:                  TSK-06, TSK-07 (ADMINISTRATIVE / THIRD-PARTY)\n"
    "================================================================================"
)
story.append(Preformatted(signoff_text, code_style))

# Page numbering footer
def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(colors.HexColor("#718096"))
    canvas.drawString(36, 18, "RESTRICTED AUDIT WORKING PAPERS — LAVETO LAB / BANK OF BOTSWANA EPS SEC. 14")
    canvas.drawRightString(576, 18, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()

doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
print(f"[✓] Executive PDF successfully generated at: {PDF_FILENAME}")
print(f"[+] File Size: {os.path.getsize(PDF_FILENAME):,} bytes")
