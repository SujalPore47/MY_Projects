import io
import numpy as np
import subprocess
import traceback
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch

def convert_webm_to_wav(audio_bytes):
    """Convert WebM bytes to WAV bytes using ffmpeg."""
    try:
        # Prepare the input and output buffer for ffmpeg
        input_audio = io.BytesIO(audio_bytes)
        output_audio = io.BytesIO()

        # Run ffmpeg to convert WebM to WAV
        process = subprocess.run(
            ['ffmpeg', '-i', 'pipe:0', '-f', 'wav', 'pipe:1'],
            input=input_audio.read(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Capture the converted audio
        output_audio.write(process.stdout)
        output_audio.seek(0)

        return output_audio
    except Exception as e:
        print(f"Error converting WebM to WAV: {e}")
        return None

def convert_bytes_to_array(audio_bytes, target_sample_rate=16000):
    """Convert audio bytes to a numpy array with the target sample rate using librosa."""
    try:
        # Convert WebM to WAV bytes
        wav_bytes_io = convert_webm_to_wav(audio_bytes)

        if wav_bytes_io is None:
            raise Exception("Failed to convert WebM to WAV.")

        # Load audio using librosa and resample to the target sample rate
        audio, original_sample_rate = librosa.load(wav_bytes_io, sr=None)
        print(f"Original Sample rate: {original_sample_rate}")

        # Resample audio to the target sample rate of 16000 Hz
        audio = librosa.resample(audio, orig_sr=original_sample_rate, target_sr=target_sample_rate)
        print(f"Resampled to: {target_sample_rate} Hz")

        return audio, target_sample_rate

    except Exception as e:
        print(f"Error converting audio bytes to array: {e}")
        traceback.print_exc()
        return None, None

def transcribe_audio(audio_bytes):
    """Transcribe audio using the Whisper model."""
    try:
        # Load Whisper processor and model
        processor = WhisperProcessor.from_pretrained("openai/whisper-tiny.en")
        model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny.en")

        # Convert audio bytes to a numpy array and resample to 16000 Hz
        audio_array, sample_rate = convert_bytes_to_array(audio_bytes)

        if audio_array is None:
            return "Failed to process audio. Please check the file format."

        # Convert numpy array to torch tensor and process the input
        input_features = processor(audio_array, sampling_rate=sample_rate, return_tensors="pt").input_features

        # Generate prediction
        prediction = model.generate(input_features)

        # Decode the predicted text
        transcription = processor.batch_decode(prediction, skip_special_tokens=True)[0]

        return transcription

    except Exception as e:
        print(f"Error during transcription: {e}")
        traceback.print_exc()
        return "Failed to transcribe audio."
