import librosa
import numpy as np
import pathlib as Path

def load_audio(path, sr=22050):
    y, sr_used = librosa.load(str(path), sr=sr, mono=True)
    return y, sr_used

def detect_rms_peaks(y, sr, topk=20, hop_length=2048, frame_length=4096):
    rms = librosa.feature.rms(
        y=y,
        frame_length=frame_length,
        hop_length=hop_length
    )[0]

    times = librosa.frames_to_time(
        np.arange(len(rms)),
        sr=sr,
        hop_length=hop_length
    )

    indices = np.argsort(rms)[-topk:][::-1]
    peaks = sorted(times[indices])

    peaks = [float(t) for t in peaks]
    return peaks