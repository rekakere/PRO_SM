import librosa
import soundfile as sf
import os
import numpy as np

#separate harmonic and percussive components:
def harmper(audio, sr):
    y_harm, y_perc = librosa.effects.hpss(audio)
    harm_path = "harmonic.wav"
    perc_path = "percussive.wav"
    sf.write(harm_path, y_harm, sr)
    sf.write(perc_path, y_perc, sr)
    return harm_path, perc_path

#basics: (tempo, SR, audio shape, chroma energy - mean (aka. harmonic energy))
def basic_info(audio, sr):
    print(f"Sample rate: {sr} Hz")
    #print(f'First 10 samples: {audio[:10]}')
    print(f'Audio shape: {audio.shape}')
    duration = librosa.get_duration(y=audio, sr=sr)
    print(f'Duration: {duration:.2f} seconds')
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    tempo = float(tempo)
    print(f'Tempo: {tempo:.2f} BPM')
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    print(f'Chroma mean values: {chroma.mean(axis=1)}')

#Chroma Ebergy Distance Function:
def avg_chroma_diff(audio1, audio2, sr1, sr2):
    chroma1 = librosa.feature.chroma_stft(y=audio1, sr=sr1)
    chroma2 = librosa.feature.chroma_stft(y=audio2, sr=sr2)
    avg_chroma1 = chroma1.mean(axis=1)
    avg_chroma2 = chroma2.mean(axis=1)
    chroma_diff = np.linalg.norm(avg_chroma1 - avg_chroma2)
    return chroma_diff

#loudness (RMS) analysis:

def loudness_analysis(audio):
    rms = librosa.feature.rms(y=audio)
    #print(f'RMS Mean: {np.mean(rms)}', f'RMS Std Dev: {np.std(rms)}')
    return np.mean(rms), np.std(rms)

#brightness (spectral centroid) analysis:
def brightness_analysis(audio, sr):
    spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)
    return np.mean(spectral_centroid), np.std(spectral_centroid)

#onset strength (percussive elements) analysis: #danceability proxy
def onset_strength_analysis(audio, sr):
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    return np.mean(onset_env), np.std(onset_env)

#zero crossing rate analysis:
def zcr_analysis(audio):
    zcr = librosa.feature.zero_crossing_rate(y=audio)
    return np.mean(zcr), np.std(zcr)