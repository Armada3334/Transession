import os
import subprocess
import wave
import json
from vosk import Model, KaldiRecognizer

def convert_mp4_to_wav(input_path, wav_path):
    """Convert .mp4 to mono WAV with 16000 Hz sample rate."""
    print(f"Converting {input_path} to {wav_path}...")
    command = [
        "ffmpeg", "-i", input_path,  # Input file
        "-ar", "16000",              # Sample rate 16000 Hz
        "-ac", "1",                  # Mono channel
        wav_path,                    # Output file
        "-y"                         # Overwrite if exists
    ]
    subprocess.run(command, check=True)
    print("Conversion completed.")

def transcribe_audio(wav_path, model_path, output_path):
    """Transcribe audio from WAV and save it to the output path."""
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    with wave.open(wav_path, "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            raise ValueError("Audio must be WAV format mono PCM with 16000 Hz sample rate.")

        transcript = ""
        print("Transcribing audio...")
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                transcript += result.get("text", "") + " "

        final_result = json.loads(recognizer.FinalResult())
        transcript += final_result.get("text", "")

        with open(output_path, 'w') as f:
            f.write(transcript.strip())

        print(f"Transcription completed and saved to {output_path}")

def main(input_mp4, output_txt, model_path="vosk-model-small-en-us-0.15"):
    wav_path = "audio.wav"  # Temporary WAV file path

    try:
        convert_mp4_to_wav(input_mp4, wav_path)
        transcribe_audio(wav_path, model_path, output_txt)
    finally:
        # Clean up the temporary WAV file
        if os.path.exists(wav_path):
            os.remove(wav_path)
            print(f"Deleted temporary file {wav_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert MP4 to WAV and transcribe it using Vosk.")
    parser.add_argument("input_mp4", help="Path to the input MP4 file")
    parser.add_argument("output_txt", help="Path to the output transcript text file")
    args = parser.parse_args()

    main(args.input_mp4, args.output_txt)
