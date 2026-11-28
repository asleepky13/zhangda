"""Trim dead air from the generated MP3 clips without re-encoding.

The TTS service pads every clip with ~0.2 s of silence before and ~0.7 s after the speech (about 40% of a short clip).
Each MPEG frame's side info carries big_values and global_gain: digital silence has big_values 0, near-silence a
low gain (speech sits around 150-200; 140 measured to cut ~30% with no speech lost), so we can find the speech without decoding and cut whole frames. A few silent frames are kept on each side (the first
kept frame may borrow bytes from the frames before it through the bit reservoir).

  python -I tools/trim_audio.py            # every clip in data/voice older than a minute (idempotent)
  from trim_audio import trim; trim(path)  # used by make_audio.py right after each clip is saved
"""
import os, sys, glob, time

BR = {1: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160], 0: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]}
SR = {1: [22050, 24000, 16000], 0: [44100, 48000, 32000]}
LEAD, TAIL, QUIET = 2, 8, 140  # frames kept before / after the speech; global_gain below this is near-silence

def frames(b):
    i, out = 0, []
    while i + 4 <= len(b):
        if b[i] != 0xFF or (b[i + 1] & 0xE0) != 0xE0: return None  # not a plain frame stream: leave the file alone
        lsf = 0 if (b[i + 1] >> 3) & 1 else 1          # 1 = MPEG-2/2.5 (one granule per frame)
        layer = (b[i + 1] >> 1) & 3
        bri, sri, pad = b[i + 2] >> 4, (b[i + 2] >> 2) & 3, (b[i + 2] >> 1) & 1
        if layer != 1 or bri in (0, 15) or sri == 3: return None
        n = (72 if lsf else 144) * BR[lsf][bri] * 1000 // SR[lsf][sri] + pad
        mono = (b[i + 3] >> 6) == 3
        side = i + 4 + (0 if b[i + 1] & 1 else 2)
        if not (lsf and mono): return None  # the TTS clips are MPEG-2 mono; anything else is left alone
        bits = int.from_bytes(b[side:side + 5], 'big')
        # MPEG-2 mono side info: main_data_begin(8) private(1) part2_3_length(12) big_values(9) global_gain(8)
        bv, gain = (bits >> 10) & 0x1FF, (bits >> 2) & 0xFF
        out.append((i, n, bv == 0 or gain < QUIET)); i += n
    return out

def trim(path):
    b = open(path, 'rb').read()
    fs = frames(b)
    if not fs or len(fs) < 12: return 0
    loud = [k for k, f in enumerate(fs) if not f[2]]
    if not loud: return 0
    a, z = max(0, loud[0] - LEAD), min(len(fs), loud[-1] + 1 + TAIL)
    if a == 0 and z == len(fs): return 0
    nb = b[fs[a][0]:fs[z - 1][0] + fs[z - 1][1]]
    open(path, 'wb').write(nb)
    return len(b) - len(nb)

if __name__ == '__main__':
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'voice')
    saved, n, now = 0, 0, time.time()
    for f in glob.glob(os.path.join(root, '*.mp3')):
        if now - os.path.getmtime(f) < 60: continue   # still being written by make_audio
        s = trim(f); saved += s; n += 1 if s else 0
    print(f'trimmed {n} clips, saved {saved / 1e6:.1f} MB')
