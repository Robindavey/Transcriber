# Transcriber

A comprehensive AI-powered transcription and content processing application that transforms various media and document types into structured notes and podcast scripts.

## Features

### File Processing Support
- **Audio Files**: MP3, WAV, FLAC, MP4, M4A, AAC - Automatic transcription using Vosk
- **Documents**: PDF, DOCX - Text extraction and parsing
- **Images**: JPG, JPEG, PNG, GIF, BMP - OCR text extraction from screenshots/photos
- **Spreadsheets**: XLSX - Tabular data conversion to text
- **Data Files**: CSV - Structured data formatting
- **Text Files**: TXT - Direct processing

### AI Processing Pipeline
- **Reconstruction**: Clean and reconstruct extracted text using Ollama/Llama2
- **Notes Generation**: Create structured notes with main topics, key points, and action items
- **Podcast Scripts**: Generate conversational podcast scripts from content
- **Text-to-Speech**: Convert scripts to audio using Piper TTS

### Web Interface
- Project-based organization
- Drag-and-drop file uploads
- Real-time processing status
- File management and downloads
- Responsive web UI

## Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg (for audio processing)
- Tesseract OCR (for image processing)
- Ollama with Llama2 model
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Transcriber
   ```

2. **Use the Makefile for easy setup**
   ```bash
   make install
   ```

   This will:
   - Create a virtual environment
   - Install all Python dependencies
   - Install system dependencies (Tesseract OCR)

3. **Manual installation (alternative)**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   sudo apt install tesseract-ocr ffmpeg
   ```

### Setup AI Models

1. **Install Ollama** (for text processing)
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama2:7b
   ```

2. **Download Vosk models** (for transcription)
   - Place models in `data/models/` directory
   - Recommended: `vosk-model-en-us-0.42-gigaspeech` for English

3. **Piper TTS models** (for text-to-speech)
   - Already included in `data/piper-voices/`

## Usage

### Starting the Application

```bash
make start
```

Or manually:
```bash
source .venv/bin/activate
python app.py
```

Access at: http://localhost:5000

### Basic Workflow

1. **Create a Project**: Click "New Project" and give it a name
2. **Upload Files**: Drag and drop or browse to upload supported files
3. **Process Content**: Click "Process to Notes" to generate structured notes
4. **Generate Audio**: Click "Generate TTS" to create podcast audio from scripts

### File Organization

Each project contains:
```
project_name/
├── uploads/     # Original uploaded files
├── raw/         # Extracted text (raw_text.txt)
├── audio/       # Generated audio files
├── notes/       # Processed notes (fullNotes.md, ShortendNotes.md)
├── scripts/     # Podcast scripts (script.txt)
└── transcripts/ # Additional transcripts
```

## Configuration

### Environment Variables
- `OLLAMA_HOST`: Ollama server address (default: localhost:11434)
- `SECRET_KEY`: Flask session secret key

### Model Configuration
- Vosk models in `data/models/`
- Piper voices in `data/piper-voices/`
- Prompts in `prompts/` directory (organized by file type)

## API Endpoints

- `GET /` - Projects dashboard
- `POST /create_project` - Create new project
- `POST /upload/<project>` - Upload files
- `POST /process/<project>` - Process to notes
- `POST /generate-tts/<project>` - Generate audio
- `GET /download-project/<project>` - Download entire project

## Development

### Project Structure
```
├── app.py              # Main Flask application
├── src/                # Source modules
│   ├── transcription.py # Audio transcription
│   ├── pdf_tool.py     # PDF processing
│   ├── image_tool.py   # OCR processing
│   ├── docx_tool.py    # Word document processing
│   ├── xlsx_tool.py    # Excel processing
│   ├── csv_tool.py     # CSV processing
│   └── tts.py          # Text-to-speech
├── templates/          # HTML templates
├── static/             # CSS/JS assets
├── prompts/            # AI processing prompts
├── data/               # Models and project data
└── requirements.txt    # Python dependencies
```

### Adding New File Types

1. Create a processing module in `src/`
2. Add file extensions to `ALL_EXTENSIONS` in `app.py`
3. Add upload handler in the `/upload` route
4. Create type-specific prompts in `prompts/`

### Testing

```bash
make test
```

## Deployment

### Production Setup

1. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set up as a system service**
   ```bash
   sudo cp scripts/transcriber.service /etc/systemd/system/
   sudo systemctl enable transcriber
   sudo systemctl start transcriber
   ```

3. **Use the Makefile for updates**
   ```bash
   make update  # Safe zero-downtime updates
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## Troubleshooting

### Common Issues

1. **TTS fails with pathvalidate error**
   ```bash
   source .venv/bin/activate
   pip install pathvalidate
   ```

2. **OCR not working**
   ```bash
   sudo apt install tesseract-ocr
   ```

3. **Audio transcription fails**
   - Ensure Vosk model is downloaded
   - Check audio file format compatibility

4. **Ollama connection issues**
   ```bash
   ollama serve  # Start Ollama server
   ```

### Logs

```bash
make logs  # View application logs
tail -f app.log  # Follow logs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review application logs
- Open an issue on GitHub

---

**Version:** v1.0.0