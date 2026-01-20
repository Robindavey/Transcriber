import os
import re
import wave
import json
import subprocess
from vosk import Model, KaldiRecognizer

def convert_audio(input_file):
    if input_file.endswith('.wav'):
        wav_file = input_file
    else:
        if not os.path.isfile(input_file):
            print(f"File {input_file} does not exist.")
            return None, None

        if input_file.endswith('.mp3'):
            wav_file = input_file.removesuffix('.mp3') + '.wav'
        elif input_file.endswith('.flac'):
            wav_file = input_file.removesuffix('.flac') + '.wav'
        elif input_file.endswith('.mp4'):
            wav_file = input_file.removesuffix('.mp4') + '.wav'
            command = f"ffmpeg -y -i {input_file} -vn -ar 16000 -ac 1 {wav_file}"
        else:
            print("Unsupported file type.")
            return None, None

        command = f"ffmpeg -y -i {input_file} -ar 16000 -ac 1 {wav_file}"
        print(f"Executing command: {command}")
        os.system(command)
        print("Conversion successful.")

    chunks_dir = "chunks"
    os.makedirs(chunks_dir, exist_ok=True)

    # Silence detection
    cmd = [
        "ffmpeg", "-i", wav_file,
        "-af", "silencedetect=noise=-30dB:d=0.8",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stderr

    silence = re.findall(r"silence_(start|end): (\d+\.\d+)", output)
    times = [float(t[1]) for t in silence]
    pairs = list(zip(times[::2], times[1::2]))

    # If no silence detected, use full file as one chunk
    if not pairs:
        print("No silence detected. Using full file as one chunk.")
        chunk_path = os.path.join(chunks_dir, "chunk_full.wav")
        subprocess.run([
            "ffmpeg", "-y", "-i", wav_file,
            "-ar", "16000", "-ac", "1",
            chunk_path
        ])
        return wav_file, [chunk_path]

    chunk_paths = []
    for i, (start, end) in enumerate(pairs):
        chunk_path = os.path.join(chunks_dir, f"chunk_{i}.wav")
        subprocess.run([
            "ffmpeg", "-y", "-i", wav_file,
            "-ss", str(start), "-to", str(end),
            "-ar", "16000", "-ac", "1",
            chunk_path
        ])
        chunk_paths.append(chunk_path)

    return wav_file, chunk_paths


def demoVosk(audioFile, output_path="Transcripts/transcription.txt"):
    wav_file, chunks = convert_audio(audioFile)

    if wav_file is None or chunks is None:
        print("Conversion failed.")
        return

    model = Model("models/vosk-model-en-us-0.42-gigaspeech")

    transcript = []
    current_time = 0.0

    for chunk in chunks:
        wf = wave.open(chunk, "rb")
        rec = KaldiRecognizer(model, wf.getframerate())

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)

        text = json.loads(rec.FinalResult()).get("text", "")
        duration = wf.getnframes() / wf.getframerate()

        transcript.append({
            "start": current_time,
            "end": current_time + duration,
            "text": text
        })
        current_time += duration

    def format_time(seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    output = ""
    next_marker = 5 * 60

    for seg in transcript:
        if seg["text"].strip() == "":
            continue

        while seg["start"] >= next_marker:
            output += f"\n\n[{format_time(next_marker)}]\n"
            next_marker += 5 * 60

        output += seg["text"] + "\n\n"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(output)

    print(f"Saved transcription to: {output_path}")


if __name__ == "__main__":
    demoVosk("testAudio/testm4.mp4")
