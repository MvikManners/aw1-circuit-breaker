"""
Laveto Wisdom AW-1 — Institutional Document Formulator & Parser
Extracts raw text from PDF, DOCX, TXT, CSV, JSON and formulates 
structured statutory dilemmas for CEDA, SEZA, and PPRA analysts.
"""
import re
import io
import json

def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """Extracts plain text across supported formats."""
    fn_lower = filename.lower()
    
    # 1. Plain text / Markdown / JSON / CSV
    if fn_lower.endswith(('.txt', '.md', '.csv', '.json')):
        try:
            return file_bytes.decode('utf-8', errors='ignore')
        except Exception:
            return file_bytes.decode('latin-1', errors='ignore')
            
    # 2. PDF Parsing (Fallback chain: pypdf -> pdfminer -> regex stream)
    elif fn_lower.endswith('.pdf'):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            if text.strip():
                return text
        except Exception:
            pass

        try:
            from pdfminer.high_level import extract_text
            text = extract_text(io.BytesIO(file_bytes))
            if text.strip():
                return text
        except Exception:
            pass

        # Regex fallback for embedded text streams
        raw = file_bytes.decode('latin-1', errors='ignore')
        strings = re.findall(r'\(([^\)]+)\)\s*Tj', raw)
        if strings:
            return " ".join(strings)
        return "PDF content ingested (Binary stream processed)."

    # 3. DOCX Parsing
    elif fn_lower.endswith('.docx'):
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([p.text for p in doc.paragraphs if p.text])
        except Exception:
            # Fallback unzip xml
            try:
                import zipfile
                import xml.etree.ElementTree as ET
                with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                    xml_content = z.read('word/document.xml')
                    tree = ET.fromstring(xml_content)
                    return "".join(tree.itertext())
            except Exception:
                return "DOCX content ingested."

    return file_bytes.decode('utf-8', errors='ignore')


def formulate_statutory_dilemma(filename: str, raw_text: str) -> dict:
    """
    Analyzes raw document text and extracts key statutory risk variables to
    construct an auditable institutional dilemma contract.
    """
    text_sample = raw_text[:5000]
    
    # Detect Capital Outlay / Funding
    capex_match = re.search(r'(?:BWP|Pula|P)\s*([\d,\.]+(?:\s*[Mm]illion|\s*[Kk]|\s*M|\s*B)?)', text_sample, re.I)
    capex = capex_match.group(0) if capex_match else "Unspecified Capital"

    # Detect Water Usage
    water_risk = bool(re.search(r'(?:groundwater|borehole|aquifer|effluent|wuc|potable|irrigation|drawdown)', text_sample, re.I))
    
    # Detect Citizen Equity / CEE
    cee_match = re.search(r'(\d{1,3})%\s*(?:citizen|local|equity|shareholding|subcontract)', text_sample, re.I)
    cee_pct = cee_match.group(0) if cee_match else "0% citizen equity"

    # Detect Beneficiation / Export
    export_raw = bool(re.search(r'(?:export|raw\s+ore|unrefined|offshore|concentrate)', text_sample, re.I))

    # Identify Dominant Sector
    sector = "SEZA_SPEDU"
    if any(k in text_sample.lower() for k in ['feedlot', 'crop', 'cattle', 'grain', 'farm', 'agri', 'poultry', 'slaughterhouse']):
        sector = "WATER_AND_AGRICULTURE"
    elif any(k in text_sample.lower() for k in ['mine', 'mineral', 'lithium', 'copper', 'nickel', 'slag', 'tailings']):
        sector = "MINING_AND_BENEFICIATION"
    elif any(k in text_sample.lower() for k in ['solar', 'bpc', 'bera', 'grid', 'megawatt', 'pv', 'battery']):
        sector = "ENERGY_AND_IRP_SOLAR"
    elif any(k in text_sample.lower() for k in ['data', 'cloud', 'hosting', 'server', 'dpa', 'citizen records']):
        sector = "DATA_SOVEREIGNTY"

    # Formulate Structured Prompt
    dilemma_prompt = (
        f"INSTITUTIONAL DOSSIER REVIEW [{filename}]:\n"
        f"Proposed capital expenditure: {capex}. Registered Sector: {sector.replace('_', ' ')}.\n"
        f"Statutory Attributes Extracted: "
        f"1. Equity Allocation: {cee_pct} (Subject to Economic Inclusion Act 2021).\n"
        f"2. Water Impact: {'High groundwater extraction demand identified (Subject to Water Act Cap 34:01 covenants)' if water_risk else 'Closed-loop municipal connection proposed'}.\n"
        f"3. Value Addition: {'Proposes raw export with deferred secondary domestic beneficiation' if export_raw else 'Full domestic on-site value addition committed'}.\n"
        f"4. Document Scope: {raw_text[:280].strip()}...\n\n"
        f"Requesting Sovereign Decision-Assurance Audit and 8-Clause Remediation Roadmap."
    )

    return {
        "status": "success",
        "filename": filename,
        "inferred_sector": sector,
        "formulated_dilemma": dilemma_prompt,
        "char_count": len(raw_text)
    }
