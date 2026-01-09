from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services import analyze_prescription_image

# Load environment vars (API keys)
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Drug Interaction API"})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Endpoint: /api/analyze
    Method: POST
    Payload: multipart/form-data ('image')
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save temp file for OCR processing
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)

        # Core Logic
        result = analyze_prescription_image(file_path)

        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

        return jsonify({
            "status": "success",
            "data": result
        })

    except Exception as e:
        # Log error internally in production
        print(f"Server Error: {str(e)}")
        return jsonify({"error": "Analysis failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)