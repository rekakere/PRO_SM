
def wav_to_mp3(wav_file_path, mp3_file_path=None, bitrate="192k"):
    """
    Convert WAV file to MP3 using pydub
    """
    from pydub import AudioSegment
    
    # ===== ADD THESE 3 LINES =====
    AudioSegment.converter = r"C:\ffmpeg\ffmpeg\bin\ffmpeg.exe"
    AudioSegment.ffmpeg = r"C:\ffmpeg\ffmpeg\bin\ffmpeg.exe"
    AudioSegment.ffprobe = r"C:\ffmpeg\ffmpeg\bin\ffprobe.exe"
    # =============================
    
    # If no MP3 path given, create one from WAV path
    if mp3_file_path is None:
        mp3_file_path = wav_file_path.replace('.wav', '.mp3')
        mp3_file_path = mp3_file_path.replace('.WAV', '.mp3')
    
    print(f"Converting: {wav_file_path} → {mp3_file_path}")
    
    # Load WAV file
    audio = AudioSegment.from_wav(wav_file_path)
    
    # Export as MP3
    audio.export(mp3_file_path, format="mp3", bitrate=bitrate)
    
    print(f"✓ MP3 created: {mp3_file_path}")
    print(f"  Bitrate: {bitrate}")
    
    return mp3_file_path


