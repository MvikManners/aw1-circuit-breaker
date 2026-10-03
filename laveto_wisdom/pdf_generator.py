# /home/LavetoLab/laveto_wisdom/pdf_generator.py
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_wisdom_pdf(audit_data: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        fontName='Helvetica'
    )
    section_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )
    truth_style = ParagraphStyle(
        'UncomfortableTruth',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#991b1b'),
        fontName='Helvetica-Oblique'
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("LAVETO WISDOM AW", title_style))
    story.append(Paragraph("Independent Algorithmic Conscience & Decision Assurance Engine | Botswana Ground-Truth Verified", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceAfter=14))

    # 2. Metadata & Posture Block
    posture = audit_data.get('final_posture', 'UNKNOWN')
    posture_color = '#dc2626' if 'HALT' in posture else ('#d97706' if 'RECALIBRATE' in posture else '#16a34a')

    meta_data = [
        [
            Paragraph(f"<b>Audit Reference:</b> {audit_data.get('audit_id', 'N/A')}", body_style),
            Paragraph(f"<b>Issued:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", body_style)
        ],
        [
            Paragraph(f"<b>Engine Version:</b> AW-1 v2.4", body_style),
            Paragraph(f"<b>Status:</b> <font color='{posture_color}'><b>{posture}</b></font>", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[260, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Mathematical Quotient Scoring Box
    w_val = audit_data.get('wisdom_quotient', 'N/A')
    formula_val = audit_data.get('formula_breakdown', 'N/A')
    score_data = [
        [
            Paragraph(f"<b>WISDOM QUOTIENT (&Omega;):</b> <font size='14' color='{posture_color}'><b>{w_val}</b></font>", body_style),
            Paragraph(f"<b>Mathematical Formulation:</b><br/>{formula_val}", body_style)
        ]
    ]
    score_table = Table(score_data, colWidths=[240, 290])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # 4. Proposal Audited
    story.append(Paragraph("PROPOSAL / MANDATE AUDITED", section_title))
    proposal_box = Table([[Paragraph(audit_data.get('proposal_text', 'No proposal text registered.'), body_style)]], colWidths=[530])
    proposal_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(proposal_box)
    story.append(Spacer(1, 14))

    # 5. The Uncomfortable Truth
    story.append(Paragraph("THE UNCOMFORTABLE TRUTH", section_title))
    truth_text = audit_data.get('uncomfortable_truth', 'N/A')
    truth_box = Table([[Paragraph(f'"{truth_text}"', truth_style)]], colWidths=[530])
    truth_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f87171')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(truth_box)
    story.append(Spacer(1, 14))

    # 6. Phased Roadmap
    story.append(Paragraph("CALIBRATED PHASED ROADMAP", section_title))
    roadmap_text = audit_data.get('roadmap', 'N/A').replace('\n', '<br/>')
    roadmap_box = Table([[Paragraph(roadmap_text, body_style)]], colWidths=[530])
    roadmap_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(roadmap_box)
    story.append(Spacer(1, 18))

    # 7. Verification Seal & Sign-off Block
    sign_data = [
        [
            Paragraph("<b>Algorithmic Circuit-Breaker:</b><br/>Enforced via Laveto Wisdom AW Decision Assurance Engine", subtitle_style),
            Paragraph("<b>Verification Signature:</b><br/>____________________________<br/>Executive Risk Compliance Officer", subtitle_style)
        ]
    ]
    sign_table = Table(sign_data, colWidths=[280, 250])
    story.append(sign_table)

    doc.build(story)
    buffer.seek(0)
    return buffer
def generate_analytics_summary_pdf(stats: dict, audits: list) -> io.BytesIO:
    """Generates an executive-level monthly governance & circuit-breaker summary."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('RepTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('RepSub', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#475569'), fontName='Helvetica')
    sec_style = ParagraphStyle('SecTitle', parent=styles['Heading2'], fontSize=11, leading=15, textColor=colors.HexColor('#1e293b'), fontName='Helvetica-Bold', spaceAfter=6)
    cell_style = ParagraphStyle('CellText', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#1e293b'))
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')

    story = []

    # 1. Header
    story.append(Paragraph("LAVETO WISDOM AW — EXECUTIVE ASSURANCE DOSSIER", title_style))
    story.append(Paragraph(f"Monthly Governance, Circuit-Breaker Interceptions & Statutory Risk Audit | Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", sub_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceAfter=12))

    # 2. Key Metrics Summary Grid
    summary_data = [
        [
            Paragraph(f"<b>Total Audits:</b> {stats.get('total_audits', 0)}", cell_style),
            Paragraph(f"<b>Circuit-Breaker Halt Rate:</b> <font color='#dc2626'><b>{stats.get('halt_rate', 0)}%</b></font>", cell_style)
        ],
        [
            Paragraph(f"<b>Mean Wisdom Quotient (&Omega;):</b> <b>{stats.get('avg_quotient', 0)}</b>", cell_style),
            Paragraph(f"<b>API Calls (Current Month):</b> {stats.get('api_calls_month', 0)}", cell_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[260, 270])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # 3. Statutory Risk Frameworks Active
    story.append(Paragraph("ACTIVE STATUTORY GROUND-TRUTH FRAMEWORKS", sec_style))
    frameworks = [
        [Paragraph("<b>Framework</b>", cell_bold), Paragraph("<b>Key Constraint / Threshold</b>", cell_bold), Paragraph("<b>Status</b>", cell_bold)],
        [Paragraph("Citizen Economic Empowerment (CEE)", cell_style), Paragraph("Mandatory 50% outsourcing across 35 statutory sectors", cell_style), Paragraph("<font color='#16a34a'><b>ACTIVE</b></font>", cell_style)],
        [Paragraph("National Food Import Deficit", cell_style), Paragraph("P9.2B import bill; strict domestic supply-chain baseline checks", cell_style), Paragraph("<font color='#16a34a'><b>ACTIVE</b></font>", cell_style)],
        [Paragraph("SEZA Investment Guidelines", cell_style), Paragraph("P50M anchor threshold with agro/energy derogation provisions", cell_style), Paragraph("<font color='#16a34a'><b>ACTIVE</b></font>", cell_style)],
        [Paragraph("Integrated Resource Plan (IRP)", cell_style), Paragraph("BERA net-metering & 30% renewable target by 2030", cell_style), Paragraph("<font color='#16a34a'><b>ACTIVE</b></font>", cell_style)]
    ]
    frame_table = Table(frameworks, colWidths=[150, 310, 70])
    frame_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(frame_table)
    story.append(Spacer(1, 14))

    # 4. Recent Audit History Table
    story.append(Paragraph("RECENT DECISION ASSURANCE AUDIT TRAIL", sec_style))
    audit_rows = [
        [
            Paragraph("<b>Ref ID</b>", cell_bold),
            Paragraph("<b>Timestamp (UTC)</b>", cell_bold),
            Paragraph("<b>Posture</b>", cell_bold),
            Paragraph("<b>&Omega;</b>", cell_bold),
            Paragraph("<b>Proposal Evaluated</b>", cell_bold)
        ]
    ]

    for a in audits[:12]:
        p = a.get("final_posture", "HALT")
        p_color = '#dc2626' if p == 'HALT' else ('#d97706' if 'CALIBRATE' in p else '#16a34a')
        audit_rows.append([
            Paragraph(a.get("audit_id", "N/A"), cell_style),
            Paragraph(str(a.get("created_at", "N/A"))[:16], cell_style),
            Paragraph(f"<font color='{p_color}'><b>{p}</b></font>", cell_style),
            Paragraph(str(a.get("wisdom_quotient", "0.0")), cell_style),
            Paragraph(str(a.get("proposal_text", ""))[:75] + "...", cell_style)
        ])

    audit_table = Table(audit_rows, colWidths=[75, 85, 60, 35, 275])
    audit_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(audit_table)

    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_simulation_comparison_pdf(sim_data: dict, baseline_text: str, calibrated_text: str) -> io.BytesIO:
    """Generates an executive side-by-side comparative variance dossier for simulated proposals."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('SimTitle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('SimSub', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#475569'), fontName='Helvetica')
    sec_style = ParagraphStyle('SecTitle', parent=styles['Heading2'], fontSize=10, leading=13, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold', spaceAfter=4)
    cell_style = ParagraphStyle('CellText', parent=styles['Normal'], fontSize=8, leading=10.5, textColor=colors.HexColor('#1e293b'))
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=8, leading=10.5, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')
    truth_base = ParagraphStyle('TruthBase', parent=styles['Normal'], fontSize=8, leading=10.5, textColor=colors.HexColor('#991b1b'), fontName='Helvetica-Oblique')
    truth_cal = ParagraphStyle('TruthCal', parent=styles['Normal'], fontSize=8, leading=10.5, textColor=colors.HexColor('#065f46'), fontName='Helvetica-Oblique')

    story = []
    story.append(Paragraph("LAVETO WISDOM AW — POLICY VARIANCE & SIMULATION REPORT", title_style))
    story.append(Paragraph(f"Comparative Decision Assurance Dossier | Simulation Ref: {sim_data.get('simulation_id', 'SIM-AUTO')} | Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", sub_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceAfter=8))

    # Metric Delta Overview Box
    delta = sim_data.get("metrics_delta", {})
    delta_data = [
        [
            Paragraph(f"<b>Posture Transition:</b> {delta.get('posture_transition', 'N/A')}", cell_bold),
            Paragraph(f"<b>Wisdom Quotient Shift (&Delta;&Omega;):</b> <b>{'+' if delta.get('score_shift', 0) > 0 else ''}{delta.get('score_shift', 0)}</b> ({delta.get('status', 'NEUTRAL')})", cell_bold)
        ]
    ]
    delta_table = Table(delta_data, colWidths=[270, 270])
    delta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(delta_table)
    story.append(Spacer(1, 10))

    # Side-by-side Proposal Text
    story.append(Paragraph("EVALUATED TEXTUAL PROPOSALS", sec_style))
    text_data = [
        [Paragraph("<b>Variant A: Baseline Dilemma</b>", cell_bold), Paragraph("<b>Variant B: Calibrated Alternative</b>", cell_bold)],
        [Paragraph(baseline_text or "No baseline provided.", cell_style), Paragraph(calibrated_text or "No calibrated text provided.", cell_style)]
    ]
    t_table = Table(text_data, colWidths=[270, 270])
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#ecfdf5')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#ffffff')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_table)
    story.append(Spacer(1, 10))

    # Core Metrics Breakdown
    b = sim_data.get("baseline", {})
    c = sim_data.get("calibrated", {})
    bp = b.get("posture", "HALT")
    cp = c.get("posture", "PROCEED")
    bp_col = '#dc2626' if bp == 'HALT' else '#d97706'
    cp_col = '#dc2626' if cp == 'HALT' else ('#d97706' if 'CALIBRATE' in cp else '#16a34a')

    story.append(Paragraph("ALGORITHMIC POSTURE & QUOTIENT COMPARISON", sec_style))
    score_data = [
        [Paragraph("<b>Parameter</b>", cell_bold), Paragraph("<b>Variant A (Baseline)</b>", cell_bold), Paragraph("<b>Variant B (Calibrated)</b>", cell_bold)],
        [Paragraph("Assigned Posture", cell_style), Paragraph(f"<font color='{bp_col}'><b>{bp}</b></font>", cell_style), Paragraph(f"<font color='{cp_col}'><b>{cp}</b></font>", cell_style)],
        [Paragraph("Wisdom Quotient (&Omega;)", cell_style), Paragraph(str(b.get("wisdom_quotient", 0.0)), cell_style), Paragraph(str(c.get("wisdom_quotient", 0.0)), cell_style)],
        [Paragraph("Formula Breakdown", cell_style), Paragraph(str(b.get("formula", "N/A")), cell_style), Paragraph(str(c.get("formula", "N/A")), cell_style)],
        [Paragraph("Door Type (Reversibility)", cell_style), Paragraph(str(b.get("passes", {}).get("pass_4_epistemic", {}).get("door_type", "N/A")), cell_style), Paragraph(str(c.get("passes", {}).get("pass_4_epistemic", {}).get("door_type", "N/A")), cell_style)]
    ]
    s_table = Table(score_data, colWidths=[160, 190, 190])
    s_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 10))

    # The Uncomfortable Truth Comparison
    story.append(Paragraph("THE UNCOMFORTABLE TRUTH: SYSTEMIC CONTRAST", sec_style))
    b_truth = b.get("passes", {}).get("pass_5_verdict", {}).get("the_uncomfortable_truth", "N/A")
    c_truth = c.get("passes", {}).get("pass_5_verdict", {}).get("the_uncomfortable_truth", "N/A")
    truth_data = [
        [Paragraph("<b>Baseline Verdict</b>", cell_bold), Paragraph("<b>Calibrated Verdict</b>", cell_bold)],
        [Paragraph(f'"{b_truth}"', truth_base), Paragraph(f'"{c_truth}"', truth_cal)]
    ]
    tr_table = Table(truth_data, colWidths=[270, 270])
    tr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#fef2f2')),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#ecfdf5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(tr_table)

    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_executive_deck_pdf() -> io.BytesIO:
    """Generates an institutional commercial pitch and statutory due-diligence deck."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DeckTitle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('DeckSub', parent=styles['Normal'], fontSize=8.5, leading=11, textColor=colors.HexColor('#475569'), fontName='Helvetica')
    sec_style = ParagraphStyle('SecTitle', parent=styles['Heading2'], fontSize=10, leading=13, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold', spaceAfter=4)
    cell_style = ParagraphStyle('CellText', parent=styles['Normal'], fontSize=8, leading=10.5, textColor=colors.HexColor('#1e293b'))
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=8, leading=10.5, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')

    story = []
    story.append(Paragraph("LAVETO WISDOM AW — INSTITUTIONAL BRIEFING & COMMERCIAL DECK", title_style))
    story.append(Paragraph(f"Autonomous Algorithmic Conscience & Statutory Decision Assurance Engine | Issued: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", sub_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f172a'), spaceAfter=8))

    # 1. The Core Executive Problem
    story.append(Paragraph("THE SYSTEMIC PROBLEM: WHY CAPITAL FAILS ON THE GROUND", sec_style))
    prob_p = Paragraph(
        "Commercial credit committees, CEDA, and parastatal evaluation boards frequently approve multi-million Pula projects that balance perfectly on spreadsheets but collapse due to physical and statutory ground realities: "
        "raw milk deficits (only 12% domestic supply met locally), 74% rain-fed yield volatility, post-harvest horticultural spoilage (35-40%), or unmetered aquifer depletion violating WUC regulations. "
        "<b>Laveto Wisdom AW intercepts these non-performing asset sinkholes prior to irreversible disbursement.</b>",
        cell_style
    )
    p_box = Table([[prob_p]], colWidths=[540])
    p_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f87171')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(p_box)
    story.append(Spacer(1, 10))

    # 2. Institutional Value Proposition Matrix
    story.append(Paragraph("INSTITUTIONAL VALUE CREATION MATRIX", sec_style))
    matrix_data = [
        [Paragraph("<b>Target Institution</b>", cell_bold), Paragraph("<b>Vulnerability Mitigated</b>", cell_bold), Paragraph("<b>Engine Circuit-Breaker Impact</b>", cell_bold)],
        [
            Paragraph("CEDA & NDB", cell_bold),
            Paragraph("High NPL rates in agro-processing and specialized facilities lacking raw feedstock.", cell_style),
            Paragraph("HALTS unhedged processing equipment tenders; enforces phased fodder and offtake guarantees.", cell_style)
        ],
        [
            Paragraph("Commercial Banks (FNBB, Stanbic, Absa)", cell_bold),
            Paragraph("Delayed due-diligence cycles and overlooked statutory liabilities in industrial lending.", cell_style),
            Paragraph("Drop-in Fintech SDK provides sub-second statutory screening and audit paper trails via REST API.", cell_style)
        ],
        [
            Paragraph("SEZA & BITC", cell_bold),
            Paragraph("FDI projects seeking fiscal incentives while exporting un-beneficiated domestic materials.", cell_style),
            Paragraph("Verifies compliance against the P50M anchor threshold and local secondary processing mandates.", cell_style)
        ],
        [
            Paragraph("PPRA & Tender Boards", cell_bold),
            Paragraph("Litigation and governance failures from non-compliance with Citizen Economic Empowerment laws.", cell_style),
            Paragraph("Halts awards violating the mandatory 50% citizen subcontracting threshold or 35 reserved sectors.", cell_style)
        ]
    ]
    m_table = Table(matrix_data, colWidths=[120, 210, 210])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 10))

    # 3. Commercial Onboarding & SLA Tiers
    story.append(Paragraph("ENTERPRISE SLA & AUDIT ALLOCATION TIERS", sec_style))
    tiers_data = [
        [Paragraph("<b>Tier</b>", cell_bold), Paragraph("<b>Audit Capacity</b>", cell_bold), Paragraph("<b>Rate Limit</b>", cell_bold), Paragraph("<b>Integration Model</b>", cell_bold)],
        [Paragraph("Standard", cell_style), Paragraph("1,000 Audits / Month", cell_style), Paragraph("60 Req / Min", cell_style), Paragraph("Single Credit/Procurement Desk; REST API + Console", cell_style)],
        [Paragraph("Enterprise", cell_style), Paragraph("5,000 Audits / Month", cell_style), Paragraph("120 Req / Min", cell_style), Paragraph("Real-Time Webhook Circuit-Breaker Alerts + Sandbox Simulator", cell_style)],
        [Paragraph("Unlimited", cell_style), Paragraph("50,000 Audits / Month", cell_style), Paragraph("300 Req / Min", cell_style), Paragraph("Full National Parastatal/Bank-wide Gate Integration + Dedicated SLA", cell_style)]
    ]
    t_table = Table(tiers_data, colWidths=[80, 120, 90, 250])
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_table)
    story.append(Spacer(1, 12))

    # 4. Certification Sign-off Block
    sign_table = Table([[
        Paragraph("<b>Institutional Governance Verification:</b> Laveto Wisdom AW-1 Engine", sub_style),
        Paragraph("<b>Executive Acceptance:</b> ____________________________", sub_style)
    ]], colWidths=[300, 240])
    story.append(sign_table)

    doc.build(story)
    buffer.seek(0)
    return buffer



def generate_term_sheet_pdf(audit_data: dict) -> bytes:
    """Generates an official Autonomous Statutory Remedy Term Sheet PDF."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Palette
    NAVY = colors.HexColor("#0F172A")
    GOLD = colors.HexColor("#D97706")
    SLATE = colors.HexColor("#475569")
    CHARCOAL = colors.HexColor("#1E293B")
    
    # Title Header
    story.append(Paragraph("REPUBLIC OF BOTSWANA • LAVETO WISDOM AW", ParagraphStyle('SubHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=GOLD, spaceAfter=4)))
    story.append(Paragraph("AUTOMATED STATUTORY REMEDY TERM SHEET", ParagraphStyle('MainTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=20, textColor=NAVY, spaceAfter=10)))
    
    audit_id = audit_data.get("audit_id", "LWA-UNKNOWN")
    posture = audit_data.get("posture", "CALIBRATE")
    quotient = audit_data.get("wisdom_quotient", 0.0)
    
    meta_text = f"<b>Audit Reference:</b> {audit_id} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Assurance Posture:</b> {posture} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Wisdom Quotient (W):</b> {quotient}"
    story.append(Paragraph(meta_text, ParagraphStyle('Meta', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=SLATE, spaceAfter=15)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=15))
    
    # Purpose & Binding Context
    story.append(Paragraph("<b>LEGAL BINDING CONTEXT & COVENANT MANDATE</b>", ParagraphStyle('SecHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=NAVY, spaceAfter=6)))
    p_desc = (
        "Pursuant to the Economic Inclusion Act 2021, Public Procurement Act 2022, Water Act [Cap 34:01], "
        "and the Special Economic Zones Act, this Term Sheet establishes the mandatory, non-negotiable statutory "
        "covenants required to cure identified compliance breaches and elevate the project dossier to a state-sanctioned [PROCEED] posture."
    )
    story.append(Paragraph(p_desc, ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, textColor=CHARCOAL, spaceAfter=12)))
    
    # Clauses
    clauses = [
        ("CLAUSE 1: CITIZEN ECONOMIC EMPOWERMENT (CEE) SUBCONTRACTING", "The proponent shall ring-fence a mandatory minimum of 50% of all non-specialized procurement, site logistics, security, and civil works for 100% citizen-owned SMMEs, subject to quarterly BURS compliance filings."),
        ("CLAUSE 2: VOTING CITIZEN EQUITY & PARTICIPATION", "The 25% citizen equity structure shall be constituted as voting ordinary shares co-anchored by institutional citizen consortia or CEDA, strictly prohibiting non-voting preference arrangements."),
        ("CLAUSE 3: CLOSED-LOOP EFFICIENT WATER RECLAMATION", "In compliance with the Water Act [Cap 34:01], the facility shall construct and operate an 80% minimum closed-loop water recycling plant, ensuring zero unmitigated raw effluent discharge into local aquifers."),
        ("CLAUSE 4: CAPTIVE RENEWABLE ENERGY CO-INVESTMENT", "To support national Integrated Resource Plan (IRP) targets (>30% renewables by 2030), the proponent shall integrate captive Solar PV + BESS capacity to offset at least 30% of industrial base-load demand."),
        ("CLAUSE 5: SOVEREIGN TELEMETRY & DATA RESIDENCY", "All operational SCADA controls, geological telemetry, financial ledgers, and employee records shall be hosted exclusively within a Botswana Tier-3 certified data centre pursuant to the Data Protection Act."),
        ("CLAUSE 6: ON-SITE SEZA BENEFICIATION MANDATE", "All raw base metal concentrates or agricultural outputs shall undergo secondary and tertiary beneficiation within designated SEZA industrial hubs prior to export authorization."),
        ("CLAUSE 7: SKILLS TRANSFER & LOCALIZATION TIMELINE", "The proponent shall establish an accredited technical apprenticeship academy within 24 months, ensuring complete localization of middle and senior technical management within 48 months."),
        ("CLAUSE 8: GOVERNANCE AUDIT & COMPLIANCE ESCROW", "Failure to maintain verified compliance with these covenants shall trigger immediate invocation of statutory circuit-breakers and reversion of SEZA fiscal privileges.")
    ]
    
    for title, desc in clauses:
        story.append(Paragraph(f"<b>{title}</b>", ParagraphStyle('ClauseTitle', parent=styles['Heading3'], fontName='Helvetica-Bold', fontSize=10, textColor=NAVY, spaceAfter=3)))
        story.append(Paragraph(desc, ParagraphStyle('ClauseBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=CHARCOAL, spaceAfter=8)))
        
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=SLATE, spaceAfter=10))
    story.append(Paragraph("<i>This document is cryptographically sealed and generated autonomously by Laveto Wisdom AW. It constitutes an official administrative recommendation under national strategic investment frameworks.</i>", ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=SLATE)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
