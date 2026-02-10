# tts_processor.py
import subprocess
import os

def text_to_speech(text_file_path, output_wav_path):
    """
    Convert text file to speech using Piper TTS
    
    Args:
        text_file_path: Path to the input text file
        output_wav_path: Path where the WAV file will be saved
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if script exists, if not, generate it
    if not os.path.exists(text_file_path):
        print("Making podcast script...")
        import subprocess
        import tempfile
        # Extract project path: text_file_path is project/scripts/script.txt
        project_path = os.path.dirname(os.path.dirname(text_file_path))
        raw_text_path = os.path.join(project_path, "raw", "raw_text.txt")
        prompt_path = "prompts/podcast-script.txt"
        
        with open(prompt_path, "r") as f:
            prompt = f.read()
        with open(raw_text_path, "r") as f:
            text = f.read()
        input_data = prompt + "\n" + text
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(input_data)
            temp_file_path = temp_file.name
        
        try:
            with open(text_file_path, "w") as output_file:
                result = subprocess.run(["ollama", "run", "llama2:7b", "--keepalive", "0"], 
                             stdin=open(temp_file_path, "r"), stdout=output_file)
                if result.returncode != 0:
                    print(f"Ollama failed with return code {result.returncode}")
                    return False
        finally:
            os.unlink(temp_file_path)
    
    try:
        # Read the text file
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Path to your Piper voice model
        model_path = os.path.expanduser('~/Desktop/Programs/Transcriber/data/piper-voices/en_US-lessac-medium.onnx')
        
        # Run Piper TTS (note: --output-file with hyphen, not underscore)
        process = subprocess.Popen(
            ['piper', '--model', model_path, '--output-file', output_wav_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Send text to piper
        stdout, stderr = process.communicate(input=text_content.encode('utf-8'))
        
        if process.returncode == 0:
            return True
        else:
            print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False
if __name__ == "__main__":
    text_file = "data/projects/example/scripts/script.txt"  # example
    output_wav = "data/projects/example/audio/audio.wav"
    success = text_to_speech(text_file, output_wav)
    if success:
        print("Text-to-speech conversion successful.")
    else:
        print("Text-to-speech conversion failed.")