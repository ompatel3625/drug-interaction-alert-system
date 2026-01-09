import os
import json
import google.generativeai as genai
from google.cloud import vision

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_prescription_image(image_path):
    """
    Orchestrates OCR -> AI Analysis pipeline.
    """
    
    # 1. OCR Extraction
    try:
        raw_text = perform_ocr(image_path)
    except Exception as e:
        print(f"OCR Error: {e}")
        return {"error": "Failed to read image text"}

    if not raw_text or len(raw_text) < 3:
        return {
            "risk_level": "Unknown",
            "alert_message": "Could not detect readable text. Please upload a clearer image."
        }

    # 2. AI Reasoning (Gemini)
    try:
        analysis_result = get_drug_interactions(raw_text)
        return analysis_result
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "risk_level": "Unknown",
            "alert_message": "AI analysis service is temporarily unavailable."
        }

def perform_ocr(image_path):
    """
    Uses Google Cloud Vision API to detect handwriting.
    """
    client = vision.ImageAnnotatorClient()

    with open(image_path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    
    # document_text_detection is optimized for dense text/handwriting
    response = client.document_text_detection(image=image)
    
    if response.error.message:
        raise Exception(f"Vision API Error: {response.error.message}")

    return response.full_text_annotation.text

def get_drug_interactions(extracted_text):
    """
    Sends raw text to Gemini Pro for medical analysis.
    """
    model = genai.GenerativeModel('gemini-pro')

    # Strict prompt for consistent JSON output
    prompt = f"""
    Act as a clinical toxicologist and pharmacist. 
    Analyze the following text extracted from a handwritten prescription:
    
    TEXT: "{extracted_text}"

    TASKS:
    1. Identify all medicine names/active ingredients. Fix OCR typos intelligently.
    2. Analyze for potential drug-drug interactions between identified medicines.
    3. Determine the Risk Severity: Low, Medium, High, or Critical.
    4. Provide a simplified explanation for a patient (no jargon).
    5. Suggest safer alternatives ONLY if risk is High/Critical.

    OUTPUT FORMAT:
    Return ONLY a valid JSON object with these keys:
    - medicines_found (list of strings)
    - risk_level (string: Low, Medium, High, Critical)
    - risk_color (string: green, yellow, orange, red)
    - alert_message (string: brief explanation)
    - alternatives (list of strings, or empty if risk is low)
    """

    response = model.generate_content(prompt)
    
    # Clean response (remove markdown backticks if present)
    clean_json = response.text.replace("```json", "").replace("```", "").strip()
    
    return json.loads(clean_json)