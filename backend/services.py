import os
import json
import google.generativeai as genai
import PIL.Image
import time

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

RISK_COLORS = {
    "green": "#10b981", "yellow": "#f59e0b",
    "orange": "#f97316", "red": "#ef4444",
    "critical": "#b91c1c", "unknown": "#64748b"
}

def analyze_prescription_image(image_paths, user_text, language="English", conditions=None, use_mock=False):
    """
    Analyzes multiple images + user text + language + patient conditions.
    """
    if use_mock:
        return get_mock_analysis()

    try:
        inputs = []
        
        # 1. Add Prompt with new Context
        print(f"DEBUG: Generating prompt for Language: {language}") # Debug print
        base_prompt = build_prompt(user_text, len(image_paths), language, conditions)
        inputs.append(base_prompt)

        # 2. Add All Images
        for path in image_paths:
            img = PIL.Image.open(path)
            img.load() 
            inputs.append(img)
        
        # 3. Call AI
        raw_result = get_drug_interactions(inputs)
        return process_risk_analysis(raw_result)

    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "risk_level": "Unknown",
            "alert_message": f"Analysis Error: {str(e)}",
            "medicines_found": [],
            "risk_hex": RISK_COLORS["unknown"]
        }

def process_risk_analysis(data):
    risk_color_name = data.get("risk_color", "unknown").lower()
    data["risk_hex"] = RISK_COLORS.get(risk_color_name, RISK_COLORS["unknown"])
    return data

def build_prompt(user_text, image_count, language, conditions):
    """Constructs prompt aware of language and patient conditions."""
    
    # 1. User Notes Context
    context = ""
    if user_text:
        context += f"\nUSER NOTES: '{user_text}'."
    
    # 2. Patient Conditions Context (Crucial for safety)
    condition_instruction = ""
    if conditions:
        condition_instruction = f"\nCRITICAL PATIENT CONTEXT: The patient has these conditions: {conditions}. CHECK STRICTLY for contraindications against these."

    # 3. Language Context - MAKE THIS LOUD
    lang_instruction = ""
    if language and language.lower() != "english":
        lang_instruction = f"""
        IMPORTANT - LANGUAGE REQUIREMENT:
        The patient speaks {language}. 
        You MUST translate the 'alert_message' and 'alternatives' values into {language}.
        However, keep the 'medicines_found' names in English (or standard medical terms).
        """
    
    file_context = "image" if image_count <= 1 else f"{image_count} different prescription images"

    return f"""
    Act as a clinical toxicologist. Analyze this {file_context} and/or user notes.
    {context}
    {condition_instruction}
    {lang_instruction}
    
    TASKS:
    1. Read the handwriting/text from ALL images provided.
    2. Identify medicine names from ALL sources.
    3. Check for drug-drug interactions across these different prescriptions.
    4. Check for contraindications based on the CRITICAL PATIENT CONTEXT provided above.
    5. Determine Risk Severity (Low, Medium, High, Critical).
    6. Write a simple alert for the patient.

    OUTPUT JSON FORMAT:
    {{
        "medicines_found": ["Meds..."],
        "risk_level": "Level",
        "risk_color": "green/yellow/orange/red",
        "alert_message": "Simple explanation translated into {language}...",
        "alternatives": ["Alt 1 translated into {language}", "Alt 2"]
    }}
    """

def get_drug_interactions(inputs):
    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]

    for model_name in models_to_try:
        try:
            print(f"Attempting analysis with model: {model_name}...")
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            
            response = model.generate_content(inputs)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)

        except Exception as e:
            print(f"Failed with {model_name}: {e}")
            continue

    raise Exception("All models failed.")

def get_mock_analysis():
    time.sleep(2)
    return {
        "medicines_found": ["Warfarin", "Aspirin"],
        "risk_level": "Critical",
        "risk_color": "red",
        "risk_hex": RISK_COLORS["red"],
        "alert_message": "DANGER: Taking Warfarin (from Prescription A) with Aspirin (from Prescription B) significantly increases bleeding risk.",
        "alternatives": ["Consult doctor immediately", "Consider Acetaminophen"],
        "disclaimer": "AI-generated. Verify with a doctor."
    }