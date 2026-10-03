import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

dossier_bp = Blueprint('dossier_bp', __name__)

UPLOAD_FOLDER = '/home/LavetoLab/lvt_backend/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class AWDossierPromptGenerator:
    """Parses uploaded investment documents and auto-generates custom 5-Pass AW audit prompts."""

    def __init__(self):
        self.statutory_anchors = {
            "mining": "Minerals Development Framework Sec. 4 & Mines and Minerals Act",
            "agro": "National Development Plan (NDP 12) & National Food Security Policy",
            "energy": "Integrated Resource Plan (IRP) & BERA IPP Regulations",
            "seza": "Special Economic Zones Act & SPEDU Fiscal Incentive Guidelines"
        }

    def generate_audit_prompt_from_text(self, dossier_title: str, raw_text: str, sector: str) -> dict:
        text_lower = raw_text.lower()
        mentions_citizen_equity = "citizen" in text_lower or "equity" in text_lower
        mentions_beneficiation = "beneficiation" in text_lower or "processing" in text_lower or "smelting" in text_lower
        mentions_subcontracting = "subcontract" in text_lower or "sme" in text_lower or "smme" in text_lower

        anchor = self.statutory_anchors.get(sector.lower(), "Public Procurement Act 2022")

        synthesized_prompt = (
            f"Perform a rigorous 5-Pass Artificial Wisdom audit on the incoming project dossier: '{dossier_title}'. "
            f"Statutory Context Primary Anchor: {anchor}. "
            f"Extracted preliminary flags -> Citizen Equity Mentioned: {mentions_citizen_equity}, "
            f"Domestic Beneficiation Mentioned: {mentions_beneficiation}, "
            f"SMME Subcontracting Mentioned: {mentions_subcontracting}. "
            "Evaluate teleological alignment, causal system dynamics, downside asymmetry, and irreversibility risk. "
            "Determine if the proposal warrants a [HALT], [CALIBRATE], or [PROCEED] posture."
        )

        return {
            "dossier_title": dossier_title,
            "detected_sector": sector,
            "primary_statutory_anchor": anchor,
            "preliminary_flags": {
                "citizen_equity": mentions_citizen_equity,
                "beneficiation": mentions_beneficiation,
                "smme_subcontracting": mentions_subcontracting
            },
            "generated_aw_prompt": synthesized_prompt
        }

generator = AWDossierPromptGenerator()

@dossier_bp.route('/wisdom/api/v1/dossier/upload', methods=['POST'])
def upload_dossier():
    """
    Accepts multi-part form data with an institutional dossier file and target sector,
    parses the text, and returns an auto-generated AW 5-Pass audit prompt.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    sector = request.form.get('sector', 'mining')
    title = request.form.get('title', file.filename)

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Basic text extraction (supports .txt; can be extended with pypdf for PDFs)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()
    except Exception as e:
        raw_text = f"Dossier uploaded successfully. Title: {title}. Parsing binary/PDF container."

    # Generate specialized prompt
    audit_package = generator.generate_audit_prompt_from_text(
        dossier_title=title,
        raw_text=raw_text,
        sector=sector
    )

    return jsonify({
        "status": "DOSSIER_PARSED_SUCCESSFULLY",
        "file_saved_to": file_path,
        "audit_package": audit_package
    }), 200
