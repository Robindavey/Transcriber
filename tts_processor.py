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
    try:
        # Read the text file
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Path to your Piper voice model
        model_path = os.path.expanduser('~/piper-voices/en_US-lessac-medium.onnx')
        
        # Run Piper TTS
        process = subprocess.Popen(
            ['piper', '--model', model_path, '--output_file', output_wav_path],
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