import numpy as np
import soundfile as sf
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

def extract_vocals_simple(input_path, output_path):
    """
    Simple but effective vocal extraction using phase cancellation.
    Works best with stereo tracks where vocals are centered.
    """
    print(f"Loading: {input_path}")
    
    # Load audio
    try:
        data, sr = sf.read(input_path)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None
    
    print(f"Sample rate: {sr} Hz, Shape: {data.shape}")
    
    # Convert to stereo if needed
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

import os

PROJECT_ROOT = r"C:\Users\revie\OneDrive\Desktop\PRO\Sound_PRO"
DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")

file_path = os.path.join(DATA_FOLDER, "example.wav")


# RUN IT
if __name__ == "__main__":
    extract_vocals_simple(file_path, "vocals_extracted.wav")
    


#WTF
def switch_at_14_seconds(vocal_file, original_file, output_file="data/switch_at_14.wav"):
    """
    Use vocal-extracted version for first 14 seconds, 
    then continue with original FULL song
    """
    
    print(f"Loading files...")
    print(f"  Vocal file: {vocal_file}")
    print(f"  Original: {original_file}")
    
    # Load both files
    vocals, sr_v = sf.read(vocal_file)
    original, sr_o = sf.read(original_file)
    
    print(f"  Vocal file length: {len(vocals)/sr_v:.1f} seconds")
    print(f"  Original length: {len(original)/sr_o:.1f} seconds")
    
    # Make sure sample rates match
    if sr_v != sr_o:
        print(f"Warning: Different sample rates ({sr_v} vs {sr_o})")
        # We'll use original's sample rate
        sr = sr_o
    else:
        sr = sr_v
    
    # Convert mono to stereo if needed
    if len(vocals.shape) == 1:
        vocals = np.column_stack([vocals, vocals])
    if len(original.shape) == 1:
        original = np.column_stack([original, original])
    
    # Calculate 14 seconds in samples
    switch_sample = int(14.0 * sr)
    
    print(f"\n  Switch at: {switch_sample} samples ({switch_sample/sr:.1f} seconds)")
    
    # Check if vocal file is long enough
    if len(vocals) < switch_sample:
        print(f"Warning: Vocal file too short ({len(vocals)} samples)")
        switch_sample = len(vocals)
        print(f"  Adjusted switch to: {switch_sample} samples")
    
    # Create the final audio
    # Start with original (full length)
    result = original.copy()
    
    # Replace first 14 seconds with vocal-extracted version
    result[:switch_sample] = vocals[:switch_sample]
    
    print(f"\nResult:")
    print(f"  First {switch_sample/sr:.1f}s: Vocal-extracted version")
    print(f"  After {switch_sample/sr:.1f}s: Original full song")
    print(f"  Total length: {len(result)/sr:.1f} seconds")
    
    # Save
    sf.write(output_file, result, sr)
    print(f"\n✓ Saved to: {output_file}")
    
    return result, sr



# Use it


PROJECT_ROOT = r"C:\Users\revie\OneDrive\Desktop\PRO\Sound_PRO"
DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")

file_path = os.path.join(DATA_FOLDER, "ocals_extracted.wav")
file_path_2 = os.path.join(DATA_FOLDER, "vocals_extracted.wav")
file_path_3 = os.path.join(DATA_FOLDER, "mixed.wav")

