import os
from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename

from src.transcription import transcribe
from src.pdf_tool import pdf_to_text
PROJECTS_FOLDER = "data/projects"
AUDIO_EXTENSIONS = {"mp3", "wav", "flac", "mp4", "m4a", "aac"}
TEXT_EXTENSIONS = {"txt"}
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp"}
DOCUMENT_EXTENSIONS = {"docx", "doc", "xlsx", "csv"}
ALL_EXTENSIONS = AUDIO_EXTENSIONS | TEXT_EXTENSIONS | IMAGE_EXTENSIONS | DOCUMENT_EXTENSIONS

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"  # For session, if needed

os.makedirs(PROJECTS_FOLDER, exist_ok=True)


def get_file_extension(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower()


def is_audio_file(filename):
    ext = get_file_extension(filename)
    return ext in AUDIO_EXTENSIONS


def is_text_file(filename):
    ext = get_file_extension(filename)
    return ext in TEXT_EXTENSIONS
def is_pdf_file(filename):
    ext = get_file_extension(filename)
    return ext == 'pdf'

def is_supported_file(filename):
    ext = get_file_extension(filename)
    return ext in ALL_EXTENSIONS


def process_text(project_path):
    import subprocess
    import tempfile
    import os
    
    raw_text_path = os.path.join(project_path, "raw", "raw_text.txt")
    full_notes_path = os.path.join(project_path, "notes", "fullNotes.txt")
    short_notes_path = os.path.join(project_path, "notes", "ShortendNotes.txt")
    
    # Reconstruction
    with open("prompts/text/reconstruction_prompt.txt", "r") as f:
        prompt = f.read()
    with open(raw_text_path, "r") as f:
        text = f.read()
    input_data = prompt + "\n" + text
    
    # Use a temporary file for input
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write(input_data)
        temp_file_path = temp_file.name
    
    try:
        with open(full_notes_path, "w") as output_file:
            subprocess.run(["ollama", "run", "llama2:7b", "--keepalive", "0"], 
                         stdin=open(temp_file_path, "r"), stdout=output_file)
    finally:
        os.unlink(temp_file_path)
    
    # Notes
    with open("prompts/text/notes_prompt.txt", "r") as f:
        prompt = f.read()
    input_data = prompt + "\n" + text
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write(input_data)
        temp_file_path = temp_file.name
    
    try:
        with open(short_notes_path, "w") as output_file:
            subprocess.run(["ollama", "run", "llama2:7b", "--keepalive", "0"], 
                         stdin=open(temp_file_path, "r"), stdout=output_file)
    finally:
        os.unlink(temp_file_path)
    
    # Podcast script generation moved to TTS function


@app.route("/")
def index():
    return render_template("projects.html")


@app.route("/api/projects")
def get_projects():
    projects = [d for d in os.listdir(PROJECTS_FOLDER) if os.path.isdir(os.path.join(PROJECTS_FOLDER, d))]
    return jsonify({"projects": projects})


@app.route("/create_project", methods=["POST"])
def create_project():
    data = request.get_json()
    project_name = data.get("name")
    if not project_name:
        return jsonify({"error": "Project name required"}), 400
    
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    if os.path.exists(project_path):
        return jsonify({"error": "Project already exists"}), 400
    
    os.makedirs(os.path.join(project_path, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "raw"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "audio"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "notes"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(project_path, "transcripts"), exist_ok=True)
    
    return jsonify({"success": True})


@app.route("/project/<project_name>")
def project_page(project_name):
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    if not os.path.exists(project_path):
        return "Project not found", 404
    return render_template("index.html", project=project_name)


@app.route("/upload/<project_name>", methods=["POST"])
def upload(project_name):
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    if not os.path.exists(project_path):
        return jsonify({"error": "Project not found"}), 404
    
    upload_folder = os.path.join(project_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    result_text = ""
    
    # Handle different file types
    if is_audio_file(filename):
        # Transcribe audio files
        try:
            raw_text_path = os.path.join(project_path, "raw", "raw_text.txt")
            result_text = transcribe(filepath, output_path=raw_text_path)
            return jsonify({"result": result_text, "type": "audio"})
        except Exception as e:
            return jsonify({"error": f"Error transcribing audio: {str(e)}"})
    
    elif is_text_file(filename):
        # Copy text files directly to raw folder
        try:
            raw_text_path = os.path.join(project_path, "raw", "raw_text.txt")
            with open(filepath, "r", encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
            with open(raw_text_path, "w") as f:
                f.write(text_content)
            result_text = text_content
            return jsonify({"result": result_text, "type": "text"})
        except Exception as e:
            return jsonify({"error": f"Error reading text file: {str(e)}"})
    elif is_pdf_file(filename):
        try:
            raw_text_path = os.path.join(project_path, "raw", "raw_text.txt")
            result_text = pdf_to_text(filename, raw_text_path)
            return jsonify({"result": result_text, "type": "text"})
        except Exception as e:
            return jsonify({"error": f"Error reading text file: {str(e)}"})
    else:
        # Other file types - store in uploads but don't process
        return jsonify({"message": f"File '{filename}' uploaded successfully to project. Parsers for this file type will be available soon.", "type": "unsupported"})
# Add this to your app.py

from flask import send_file
from src.tts import text_to_speech

@app.route("/generate-tts/<project_name>", methods=["POST"])
def generate_tts(project_name):
    """Generate TTS from the podcast script"""
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    if not os.path.exists(project_path):
        return jsonify({"error": "Project not found"}), 404
    
    script_path = os.path.join(project_path, "scripts", "script.txt")
    output_path = os.path.join(project_path, "audio", "podcast_audio.wav")
    file_type = get_file_extension(script_path)
    # Check if script file exists
    if not os.path.exists(script_path):
        # Generate TTS
        success = text_to_speech(script_path, output_path, file_type)
        return jsonify({"error": "Script file not found"}), 404
    
    # Generate TTS
    success = True
    
    if success:
        return jsonify({"success": True, "message": "Audio generated successfully"})
    else:
        return jsonify({"error": "TTS generation failed"}), 500


@app.route("/download-tts/<project_name>", methods=["GET"])
def download_tts(project_name):
    """Download the generated TTS audio file"""
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    output_path = os.path.join(project_path, "audio", "podcast_audio.wav")
    
    if not os.path.exists(output_path):
        return jsonify({"error": "Audio file not found"}), 404
    
    return send_file(output_path, as_attachment=True, download_name="podcast_audio.wav")


@app.route("/download-project/<project_name>", methods=["GET"])
def download_project(project_name):
    """Download entire project as zip file"""
    import shutil
    import tempfile
    
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    if not os.path.exists(project_path):
        return jsonify({"error": "Project not found"}), 404
    
    # Create a temporary zip file
    temp_dir = tempfile.gettempdir()
    zip_path = os.path.join(temp_dir, f"{project_name}")
    
    # Create zip archive
    shutil.make_archive(zip_path, 'zip', project_path, '.')
    zip_file_path = f"{zip_path}.zip"
    
    try:
        return send_file(zip_file_path, as_attachment=True, download_name=f"{project_name}.zip")
    finally:
        # Clean up the temporary zip file after sending
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)


@app.route("/process/<project_name>", methods=["POST"])
def process(project_name):
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    if not os.path.exists(project_path):
        return jsonify({"error": "Project not found"}), 404
    
    process_text(project_path)
    return jsonify({"success": True, "message": "Processing completed"})


@app.route("/project/<project_name>/files/<folder>")
def get_files(project_name, folder):
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    folder_path = os.path.join(project_path, folder)
    if not os.path.exists(folder_path):
        return jsonify({"files": []})
    
    files = []
    for f in os.listdir(folder_path):
        f_path = os.path.join(folder_path, f)
        if os.path.isfile(f_path):
            size = os.path.getsize(f_path)
            files.append({"name": f, "size": size})
    
    return jsonify({"files": files})


@app.route("/project/<project_name>/notes")
def get_notes(project_name):
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    notes_path = os.path.join(project_path, "notes", "fullNotes.txt")
    if not os.path.exists(notes_path):
        return jsonify({"error": "Notes not found"}), 404
    
    with open(notes_path, "r") as f:
        notes = f.read()
    return jsonify({"notes": notes})


@app.route("/delete_project/<project_name>", methods=["DELETE"])
def delete_project(project_name):
    import shutil
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    if not os.path.exists(project_path):
        return jsonify({"error": "Project not found"}), 404
    
    shutil.rmtree(project_path)
    return jsonify({"success": True})


@app.route("/delete_file/<project_name>/<folder>/<filename>", methods=["DELETE"])
def delete_file(project_name, folder, filename):
    project_path = os.path.join(PROJECTS_FOLDER, project_name)
    file_path = os.path.join(project_path, folder, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    os.remove(file_path)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
