import google.generativeai as genai
import json
import os
from flask import current_app

# Configure your API key
genai.configure(api_key="YOUR_GOOGLE_AI_STUDIO_API_KEY")

def load_images(image_paths):
    """Loads image files from disk into the format Gemini expects."""
    images = []
    for path in image_paths:
        # Assuming paths are relative to your static folder
        full_path = os.path.join(current_app.root_path, 'static', path.lstrip('/'))
        if os.path.exists(full_path):
            with open(full_path, 'rb') as f:
                images.append({'mime_type': 'image/jpeg', 'data': f.read()})
    return images

def verify_forensic_integrity(vin_dna, image_paths):
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # The formal Forensic Analysis Prompt
    prompt = """
    You are the Laveto Sovereign Covenant AI Auditor. Your task is to analyze a set of 4 images representing a mechanical intervention:
    1. Identity (VIN/Asset verification)
    2. Fault (The diagnosed issue)
    3. Comparison (Side-by-side or diagnostic proof)
    4. Install (The completed mechanical work)

    Analyze the provided image set for technical integrity. Assign an 'audit_score' between 0.0 (Failed/Fraudulent) and 1.0 (Exemplary/Sovereign Standard).

    Evaluation Criteria:
    - Mechanical Precision: Does the Install image clearly resolve the issue shown in the Fault image?
    - Integrity: Is there clear evidence of the same vehicle (Identity) throughout all photos?
    - Documentation: Are the photos clear and sufficient to prove the work was performed?

    Output ONLY in JSON format:
    {
      "status": "VERIFIED" | "FAILED",
      "audit_score": 0.0,
      "reasoning": "Brief explanation"
    }
    """
    
    # Send prompt and loaded images to the Oracle
    response = model.generate_content([prompt] + load_images(image_paths))
    
    try:
        # Clean the response to ensure it's valid JSON
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except Exception as e:
        return {"status": "FAILED", "audit_score": 0.0, "reasoning": "AI Processing Error"}