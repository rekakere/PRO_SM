#Filter out harmonic and percussive components

def harmper(audio, sr):
    import librosa
    import soundfile as sf
    
    #harmonic and percussive components:
    y_harm, y_perc = librosa.effects.hpss(audio)
    
    #save files:
    sf.write("harmonic.wav", y_harm, sr)
    sf.write("percussive.wav", y_perc, sr)
    
    return y_harm, y_perc