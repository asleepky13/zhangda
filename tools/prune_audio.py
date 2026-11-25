"""Delete clips in data/voice that no audio index refers to (left behind when course text changes).

Run only when make_audio.py is not running: clips for the level being generated aren't in an index until it ends.
  python -I tools/prune_audio.py          # dry run: counts
  python -I tools/prune_audio.py --apply  # delete
"""
import os, sys, glob, json
VOICE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'voice')
used = set()
for f in glob.glob(os.path.join(VOICE, '*.json')):
    used.update(json.load(open(f, encoding='utf-8'))['files'].values())
orphans = [f for f in glob.glob(os.path.join(VOICE, '*.mp3')) if os.path.basename(f)[:-4] not in used]
size = sum(os.path.getsize(f) for f in orphans)
print(f'{len(used)} clips referenced, {len(orphans)} orphaned ({size / 1e6:.1f} MB)')
if '--apply' in sys.argv:
    for f in orphans: os.remove(f)
    print('deleted')
