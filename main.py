"""A web server to generate sentences using Vertex AI / Gemini on Cloud Run."""

import os
from flask import Flask, request, jsonify
import google.auth
import vertexai
from vertexai import generative_models

app = Flask(__name__)

# Initialize Vertex AI
try:
    credentials, project = google.auth.default()
    PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT') or project
    LOCATION = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')
    MODEL_NAME = os.environ.get('VERTEX_AI_MODEL', 'gemini-2.5-flash')

    if PROJECT_ID:
        vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
        model = generative_models.GenerativeModel(MODEL_NAME)
    else:
        model = None
        print("Warning: GCP Project ID could not be resolved. Vertex AI not initialized.")
except Exception as e:
    model = None
    print(f"Warning: Failed to initialize Vertex AI: {e}")

@app.route('/')
def index():
    return jsonify({
        "status": "healthy",
        "message": "Vertex AI Gemini Server is running."
    })

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if not model:
        return jsonify({
            "error": "Vertex AI is not initialized. Please configure Google Cloud Project credentials."
        }), 500

    prompt = None
    if request.method == 'POST':
        # Support JSON payload or Form data
        if request.is_json:
            data = request.get_json(silent=True) or {}
            prompt = data.get('prompt')
        else:
            prompt = request.form.get('prompt')
    else:
        prompt = request.args.get('prompt')

    if not prompt:
        return jsonify({"error": "Missing 'prompt' parameter."}), 400

    try:
        response = model.generate_content(prompt)
        return jsonify({
            "prompt": prompt,
            "response": response.text
        })
    except Exception as e:
        return jsonify({"error": f"Error generating content: {e}"}), 500

if __name__ == '__main__':
    # Local development server
    port = int(os.environ.get('PORT', 8089))
    app.run(host='0.0.0.0', port=port, debug=True)