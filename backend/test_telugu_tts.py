import torch
import numpy as np
from scipy.io.wavfile import write
from transformers import VitsModel, AutoTokenizer

MODEL_ID = "facebook/mms-tts-tel"

print("Loading Telugu tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

print("Loading Telugu speech model...")
model = VitsModel.from_pretrained(MODEL_ID)
model.eval()

text = "నమస్కారం! నేను వర్షా ఏ ఐ. ఈ రోజు వాతావరణం ఎలా ఉందో మీకు చెప్తాను."

print("Generating Telugu speech...")
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    waveform = model(**inputs).waveform.squeeze().cpu().numpy()

waveform = np.clip(waveform, -1.0, 1.0)
audio = (waveform * 32767).astype(np.int16)

output_file = "telugu_test.wav"
write(output_file, model.config.sampling_rate, audio)

print(f"Success! Audio saved to: {output_file}")
print(f"Sample rate: {model.config.sampling_rate} Hz")
