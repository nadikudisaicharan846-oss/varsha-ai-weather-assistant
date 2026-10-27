
import os
import torch
from transformers import AutoTokenizer, VitsModel

# Start with a small CPU thread count for testing.
torch.set_num_threads(min(4, os.cpu_count() or 1))


MODEL_ID = "facebook/mms-tts-tel"

_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model

    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        _model = VitsModel.from_pretrained(MODEL_ID)
        _model.eval()

    return _tokenizer, _model



def generate_telugu_audio(text: str) -> bytes:
    import io
    import time
    import numpy as np
    from scipy.io.wavfile import write

    total_start = time.perf_counter()

    # 1. Check model loading / retrieval time
    start = time.perf_counter()
    tokenizer, model = _load_model()
    load_time = time.perf_counter() - start

    # 2. Check tokenization time
    start = time.perf_counter()
    inputs = tokenizer(text[:1500], return_tensors="pt")
    tokenize_time = time.perf_counter() - start
    token_count = inputs["input_ids"].shape[1]

    # 3. Check model inference time
    start = time.perf_counter()
    with torch.inference_mode():
        waveform = model(**inputs).waveform.squeeze().cpu().numpy()
    inference_time = time.perf_counter() - start

    # 4. Check WAV conversion time
    start = time.perf_counter()
    waveform = np.clip(waveform, -1.0, 1.0)
    audio = (waveform * 32767).astype(np.int16)

    buffer = io.BytesIO()
    write(buffer, model.config.sampling_rate, audio)
    buffer.seek(0)
    result = buffer.read()
    wav_time = time.perf_counter() - start

    total_time = time.perf_counter() - total_start

    print(
        f"[Telugu TTS DEBUG] chars={len(text)}, "
        f"tokens={token_count}, "
        f"model_load={load_time:.2f}s, "
        f"tokenize={tokenize_time:.2f}s, "
        f"inference={inference_time:.2f}s, "
        f"wav={wav_time:.2f}s, "
        f"total={total_time:.2f}s"
    )

    return result
