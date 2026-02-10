import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from recieveAudioWriteTextToFile import transcribe

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"mp3", "wav", "flac"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Call your existing pipeline
        result_text = transcribe(filepath)

        return jsonify({"result": result_text})

    return jsonify({"error": "Invalid file type"}), 400
# Add this to your app.py

from flask import send_file
from tts_processor import text_to_speech

@app.route("/generate-tts", methods=["POST"])
def generate_tts():
    """Generate TTS from the podcast script"""
    script_path = "./podcastscripts/script.txt"
    output_path = os.path.join(UPLOAD_FOLDER, "podcast_audio.wav")
    
    # Check if script file exists
    if not os.path.exists(script_path):
        return jsonify({"error": "Script file not found"}), 404
    
    # Generate TTS
    success = text_to_speech(script_path, output_path)
    
    if success:
        return jsonify({"success": True, "message": "Audio generated successfully"})
    else:
        return jsonify({"error": "TTS generation failed"}), 500


@app.route("/download-tts", methods=["GET"])
def download_tts():
    """Download the generated TTS audio file"""
    output_path = os.path.join(UPLOAD_FOLDER, "podcast_audio.wav")
    
    if not os.path.exists(output_path):
        return jsonify({"error": "Audio file not found"}), 404
    
    return send_file(output_path, as_attachment=True, download_name="podcast_audio.wav")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
