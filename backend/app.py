from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services import analyze_prescription_image

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze endpoint.
    Payload: 
    - image (Multiple Files allowed)
    - description (String)
    - language (String)
    - conditions (String)
    """
    use_mock = request.args.get('mock', '').lower() == 'true'
    
    # Get Text Inputs
    user_text = request.form.get('description', '')
    language = request.form.get('language', 'English')
    conditions = request.form.get('conditions', '')

    # --- DEBUG PRINT ---
    print(f"Incoming Request -> Language: {language}, Conditions: {conditions}, Text: {user_text}")
    # -------------------

    saved_file_paths = []

    try:
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)

        # Handle Multiple Images
        if 'image' in request.files:
            files = request.files.getlist('image')
            for file in files:
                if file.filename != '':
                    file_path = os.path.join(temp_dir, file.filename)
                    file.save(file_path)
                    saved_file_paths.append(file_path)
        
        # Validation
        if not saved_file_paths and not user_text:
             return jsonify({"error": "Please provide an image or a description."}), 400

        # Process with Language & Conditions
        result = analyze_prescription_image(
            saved_file_paths, 
            user_text, 
            language=language, 
            conditions=conditions, 
            use_mock=use_mock
        )

        # Cleanup
        for path in saved_file_paths:
            if os.path.exists(path):
                os.remove(path)

        return jsonify({
            "status": "success",
            "data": result
        })

    except Exception as e:
        for path in saved_file_paths:
            if os.path.exists(path):
                os.remove(path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)