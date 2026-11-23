"""Generate the app's built-in audio for every line of course content that has no native recording.

Run after adding a unit:   python tools/make_audio.py
Needs: pip install edge-tts (uses Microsoft's neural voices; one-off generation, files are shipped with the app).
Writes data/voice/<hash>.mp3 and data/voice/index.json (text -> file). Existing files are kept, so runs are incremental.
"""
import asyncio, hashlib, json, re, glob, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(DATA, 'voice')
VOICE = 'zh-CN-XiaoxiaoNeural'
HAN = re.compile(r'[㐀-鿿]')
TONE = {c: (v, t + 1) for v, s in {'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì', 'o': 'ōóǒò', 'u': 'ūúǔù', 'ü': 'ǖǘǚǜ'}.items() for t, c in enumerate(s)}

def syl_key(p):
    """'lǜ' -> 'lv4', 'ma' -> 'ma5' (same naming as audio-cmn)."""
    base, tone = '', 5
    for ch in p.lower():
        if ch in TONE: base += TONE[ch][0]; tone = TONE[ch][1]
        elif ch.isalpha() or ch == 'ü': base += ch
    base = re.sub(r'^([jqxy])ü', r'\1u', base).replace('ü', 'v')
    return f'{base}{tone}'

def collect():
    cmn = json.load(open(os.path.join(DATA, 'audio.json'), encoding='utf-8'))
    words, syls = set(cmn['words']), set(cmn['syl'])
    idx = json.load(open(os.path.join(DATA, 'index.json'), encoding='utf-8'))
    texts = {'你好，我们开始学习吧。', '嗯？你说什么？'}
    for st in idx['stages']:
        for f in st['units']:
            u = json.load(open(os.path.join(DATA, f), encoding='utf-8'))
            for it in u['items']:
                s = it['s']
                han = HAN.findall(s)
                for e in it.get('ex', []): texts.add(e['zh'])
                if len(han) == 1 and s.strip() == han[0]:
                    k = syl_key(it['p'].split()[0])
                    # human syllable recording exists, or neutral-tone single char (app plays its example), or a radical
                    if k in syls or k.endswith('5') or it['k'] == 'rad': continue
                elif s in words: continue
                if han: texts.add(s)
            for t in u.get('texts', []):
                for l in t['lines']: texts.add(l['zh'])
                for q in t.get('qs', []):
                    if q.get('ans') and HAN.search(q['ans']): texts.add(q['ans'])
            for x in u.get('exercises', []):
                if x['type'] == 'order': texts.add(x['zh'])
                if x['type'] == 'translate': texts.add(x['a'][0])
                if x['type'] == 'zaoju': texts.update(x['models'])
            sc = u.get('scenario')
            if sc:
                for n in sc['nodes'].values():
                    texts.add(n['npc'])
                    for o in n.get('opts', []): texts.add(o['zh'])
    return sorted(t.strip() for t in texts if HAN.search(t))

async def main():
    import edge_tts
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, 'index.json')
    index = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {'voice': VOICE, 'files': {}}
    todo = []
    for t in collect():
        h = hashlib.sha1(t.encode('utf-8')).hexdigest()[:12]
        index['files'][t] = h
        if not os.path.exists(os.path.join(OUT, h + '.mp3')): todo.append((t, h))
    print(f'{len(index["files"])} lines, {len(todo)} to generate')
    sem = asyncio.Semaphore(6); fails = []
    async def one(t, h):
        async with sem:
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(t, VOICE, rate='-5%').save(os.path.join(OUT, h + '.mp3')); return
                except Exception as e:
                    await asyncio.sleep(2 + attempt * 3); err = e
            fails.append((t, str(err)))
    await asyncio.gather(*(one(t, h) for t, h in todo))
    for t, e in fails: index['files'].pop(t, None); print('FAILED', t, e)
    # drop entries whose text no longer appears in the course
    live = set(collect())
    index['files'] = {k: v for k, v in sorted(index['files'].items()) if k in live}
    json.dump(index, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    size = sum(os.path.getsize(os.path.join(OUT, v + '.mp3')) for v in index['files'].values())
    print(f'done: {len(index["files"])} files, {size / 1e6:.1f} MB, {len(fails)} failed')
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    asyncio.run(main())
