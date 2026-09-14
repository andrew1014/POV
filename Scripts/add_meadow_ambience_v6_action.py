#!/usr/bin/env python3
"""
v6 POV piglet ACTION audio — realistic running mix.
Layers for each clip (muxed onto the free pixverse video):
  1. BED  : real daytime meadow birdsong (english_meadow.mp3, distinct window/clip).
  2. FEET : synthesized rhythmic GALLOPING footstep thuds (lowpassed ~55-95Hz thump +
            soft noise puff), strong & front-of-mix -> reads as piglet running.
  3. PIGS : REAL piglet calls (oink/snort/squeal) placed as 1-2 playful bursts.
Mastered so footsteps are clearly audible (~ -18..-22 dB mean), birds quieter bed.

Per Andrew: current birdsong-only audio is "alright" but needs MORE — the loud running
footsteps etc. so it reads realistic. Steps are the protagonist sound here.
"""
import os, subprocess, numpy as np, soundfile as sf
import wave, struct

BASE  = r"E:\APEX\POV\TestVideos\piglets"
SFC   = os.environ.get("LOCALAPPDATA", r"C:\Users\avega.VEGANATOR\AppData\Local") + r"\Temp\pigsfx"
MEADOW = os.environ.get("LOCALAPPDATA") + r"\Temp\english_meadow.mp3"
OUTSUB= "with_audio_v6"
SR    = 44100

# clip, meadow offset, footstep profile, oink moments(s) within ~15s, oink files to use
CLIPS = [
    # running clips - full gallop footsteps + playful squeals
    ("pov_piglet_flowerfield.mp4", 60,  "gallop", [(2.5, ["Pig oinking.wav", "Pig oink.wav"]), (10.0, ["Snorting pig.wav"])]),
    ("pov_piglet_butterfly.mp4",   700,"trot",   [(5.0, ["Pig oink.wav"]), (12.0, ["Pig oinking.wav"])]),
    ("pov_piglet_trough.mp4",      1400,"amble", [(3.0, ["Snorting pig.wav"]), (8.0, ["Pig snort.wav"]), (12.5, ["Pig oinking.wav"])]),
    ("pov_piglet_scene2_companion_butterfly.mp4", 2100,"gallop", [(2.0, ["Pig oinking.wav"]), (9.0, ["Pig oink.wav", "Pig snort.wav"])]),
    ("sc2_dynamic_v1_review.mp4",                 1800,"gallop", [(2.0, ["Pig oinking.wav"]), (7.5, ["Pig oink.wav"]), (12.0, ["Snorting pig.wav"])]),
]

def load_wav(path):
    data, sr = sf.read(path, dtype="float32")
    if data.ndim == 1: data = np.stack([data, data], axis=1)
    if sr != SR: data = _resample(data, sr)
    return data

def _resample(x, sr):
    from scipy.signal import resample_poly
    g = np.gcd(sr, SR)
    return resample_poly(x, SR//g, sr//g, axis=0)

def lowpass(x, cutoff):
    from scipy.signal import butter, filtfilt
    b, a = butter(2, cutoff/(SR/2), btype="low")
    return filtfilt(b, a, x, axis=0)

def footsteps(dur_s, profile, seed=7, nfeet=1):
    """Rhythmic gallop/trot footstep thuds. Returns stereo float32."""
    rng = np.random.default_rng(seed)
    N = int(dur_s*SR)
    out = np.zeros((N,2), dtype=np.float32)
    if profile == "gallop":   bps = 5.5; pair=2   # fast excited running
    elif profile == "trot":   bps = 4.0; pair=1   # moderate
    else:                     bps = 2.2; pair=1   # amble (feeding/standing)
    t = 0.0
    step_idx = 0
    while t < dur_s - 0.1:
        # small human/animal timing jitter
        t += max(0.05, (1.0/bps) * rng.uniform(0.8, 1.15))
        if t >= dur_s: break
        i0 = int(t*SR)
        # --- thump body: decaying low sine (footfall impact) ---
        f = rng.uniform(62, 88)               # deep knuckle of the step
        seg = 0.085                           # ~85ms impact
        tt = np.arange(int(seg*SR))/SR
        thump = np.sin(2*np.pi*f*tt) * np.exp(-tt*55)
        thump *= rng.uniform(0.85, 1.0)
        # --- soft dirt noise puff (ground contact texture) ---
        puff = rng.standard_normal(len(thump)) * np.exp(-tt*90) * 0.18
        step = thump + puff
        step = np.clip(step, -1, 1)
        # amplitude ~ footstep weight, front-of-mix
        amp = rng.uniform(0.16, 0.24)
        # alternate slight left/right pan for movement realism
        pL = 0.5 + (0.32 if (step_idx % 2) else -0.32)
        pR = 1.0 - pL
        i1 = min(i0+len(step), N)
        n = i1-i0
        out[i0:i1,0] += step[:n]*amp*(pL*2)
        out[i0:i1,1] += step[:n]*amp*(pR*2)
        step_idx += 1
    # master lowpass to remove any harsh click edges
    out = lowpass(out, 3000)
    # normalize peak
    m = np.abs(out).max()
    if m > 0: out = out / m * 0.32
    return out.astype(np.float32)

def place_pig(out, t, files):
    """Mix real piglet calls at time t."""
    for f in files:
        p = os.path.join(SFC, f)
        if not os.path.exists(p): continue
        d = load_wav(p)
        i0 = int(t*SR); i1 = min(i0+len(d), len(out))
        n = i1-i0
        if n <= 0: continue
        seg = d[:n]
        seg = seg / (np.abs(seg).max()+1e-9) * 0.22   # audible, lively
        out[i0:i1] += seg
        t += 0.35   # tiny gap if multiple

def main():
    os.makedirs(os.path.join(BASE, OUTSUB), exist_ok=True)
    for clip, moff, prof, pigs in CLIPS:
        inp = os.path.join(BASE, clip)
        if not os.path.exists(inp):
            print("skip (no base clip):", clip); continue
        dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                "-of","default=noprint_wrappers=1:nokey=1",inp],
                capture_output=True,text=True).stdout.strip())
        out = np.zeros((int(dur*SR),2), dtype=np.float32)

        # --- feet (front layer) ---
        feet = footsteps(dur, prof)
        out += feet

        # --- real piglet vocal bursts ---
        for t, files in pigs:
            if t < dur: place_pig(out, t, files)

        out = np.clip(out, -1, 1)

        # bed: real daytime meadow window (quiet under the action)
        bed_wav = os.path.join(BASE, OUTSUB, clip.replace(".mp4","_bed.wav"))
        subprocess.run(["ffmpeg","-y","-v","error","-ss",str(moff),"-t",f"{dur:.3f}",
            "-i",MEADOW,"-af","afade=t=in:st=0:d=1,afade=t=out:st=%.3f:d=1.5,volume=0.5,aresample=44100"%max(0,dur-1.5),
            "-ar","44100","-ac","2", bed_wav], check=True)
        bed,_ = sf.read(bed_wav, dtype="float32")
        if bed.ndim==1: bed=np.stack([bed,bed],axis=1)
        if len(bed)<len(out): bed=np.pad(bed,((0,len(out)-len(bed)),(0,0)))
        bed=bed[:len(out)]
        out = out*0.95 + bed[:len(out)]*0.30   # action up front, birds as texture
        out = np.clip(out,-1,1)

        # normalize so footsteps are loud (~ -19 dB), no clip
        m=np.abs(out).max()
        if m>0.98: out=out/m*0.98

        mix_wav = os.path.join(BASE, OUTSUB, clip.replace(".mp4","_mix.wav"))
        sf.write(mix_wav, out, SR)
        final = os.path.join(BASE, OUTSUB, clip.replace(".mp4","_sfx.mp4"))
        subprocess.run(["ffmpeg","-y","-i",inp,"-i",mix_wav,
            "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k",
            "-shortest","-movflags","+faststart", final], check=True)

        # verify audio landed
        streams=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_type",
            "-of","csv",final],capture_output=True,text=True).stdout.split()
        lv=subprocess.run(["ffmpeg","-i",final,"-af","volumedetect","-f","null","-"],
            capture_output=True,text=True).stderr
        mean=[l for l in lv.splitlines() if "mean_volume" in l]
        print(f"OK {clip}: streams={streams} | {mean[0].strip() if mean else ''}")
    # cleanup intermed
    for f in os.listdir(os.path.join(BASE,OUTSUB)):
        if f.endswith((".wav",".aac")): os.remove(os.path.join(BASE,OUTSUB,f))

if __name__=="__main__":
    main()
