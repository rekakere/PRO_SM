def extract_vocals_simple(input_path, output_path):
   
    print(f"Loading: {input_path}")
    
    try:
        data, sr = sf.read(input_path)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None
    
    #print(f"Sample rate: {sr} Hz, Shape: {data.shape}")
    
    # convert to stereo if mono
    if len(data.shape) == 1:
        print("Mono file detected - converting to stereo")
        data = np.column_stack([data, data])
    
    # Method 1: Center channel extraction (vocals are often in center)
    # Center = Left - Right (removes panned instruments)
    center_channel = data[:, 0] - data[:, 1]
    
    # Method 2: Alternatively, try Mid-Side processing
    mid = (data[:, 0] + data[:, 1]) / 2  # Center
    side = (data[:, 0] - data[:, 1]) / 2  # Sides
    
    # Combine methods for better results
    vocals = 0.7 * center_channel + 0.3 * mid
    
    # Apply bandpass filter for vocal frequencies
    # Human voice: ~85Hz to 255Hz (male), 165Hz to 255Hz (female)
    nyquist = sr / 2
    low_cut = 85 / nyquist    # Lower bound for vocals
    high_cut = 1000 / nyquist  # Upper bound (can adjust)
    
    if low_cut < 1.0 and high_cut > 0:
        b, a = signal.butter(4, [low_cut, high_cut], btype='band')
        vocals = signal.filtfilt(b, a, vocals)
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(vocals))
    if max_val > 0:
        vocals = vocals / max_val * 0.9  # 0.9 to avoid clipping
    
    # Save result
    sf.write(output_path, vocals, sr)
    print(f"✓ Saved vocals to: {output_path}")
    
    # Also save instrumental (original - vocals)
    instrumental = data[:, 0] + data[:, 1] - vocals
    max_val = np.max(np.abs(instrumental))
    if max_val > 0:
        instrumental = instrumental / max_val * 0.9
    
    base, _ = os.path.splitext(output_path)
    inst_path =  base + "_instrumental.wav"
    sf.write(inst_path, instrumental, sr)
    print(f"✓ Saved instrumental to: {inst_path}")
    
    return vocals, sr




