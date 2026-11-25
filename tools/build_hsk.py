"""Build the HSK 3.0 track (levels 1-6 and the 7-9 band) from open data.

Inputs (not published, see tools/raw/):
  complete.json  github.com/drkameleon/complete-hsk-vocabulary (MIT): words, levels, pinyin, meanings, radicals
  cmn.txt        Tatoeba Chinese-English pairs via manythings.org/anki (CC BY 2.0 FR)
Outputs: data/hsk/hsk<L>.json (one pack per level; 7-9 split in three parts) and the HSK stages in data/index.json.

Flow: words in each level go most-frequent first, 40 to a unit, 8 to a lesson. Example sentences are chosen so their
characters come from this unit and earlier ones (falling back to the level, then to all HSK), so every unit builds on
the last. Run: python -I tools/build_hsk.py
"""
import json, os, re, sys, random, math, collections
sys.stdout.reconfigure(encoding='utf-8')
random.seed(7)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, DATA = os.path.join(ROOT, 'tools', 'raw'), os.path.join(ROOT, 'data')
HAN = re.compile(r'[㐀-鿿]')
PUNCT = set('，。！？、：；“”‘’（）《》…—·「」『』')
UNIT = 40
TONES = {'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì', 'o': 'ōóǒò', 'u': 'ūúǔù', 'ü': 'ǖǘǚǜ'}
UNMARK = {c: v for v, s in TONES.items() for c in s}
POS = {'n': 'n', 'nr': 'n', 'ns': 'n', 'nt': 'n', 'nz': 'n', 'nw': 'n', 't': 'n', 's': 'n', 'f': 'n', 'j': 'n', 'v': 'v', 'vn': 'v', 'vd': 'v', 'a': 'adj', 'ad': 'adj', 'an': 'adj', 'b': 'adj', 'z': 'adj',
       'd': 'adv', 'r': 'pron', 'm': 'num', 'mq': 'num', 'q': 'mw', 'p': 'prep', 'c': 'conj', 'u': 'part', 'y': 'part', 'k': 'part', 'e': 'interj', 'o': 'interj', 'i': 'phrase', 'l': 'phrase', 'h': 'prefix'}
RADMAP = dict(zip('⺼⺮⻊⻖⻏⺡⺘⺾⻗⺗⺌⻌⻍⺍⺈⺊⺧⺨⺶⺹⻂⻆⻈⻐⻓⻔⻘⻙⻚⻛⻜⻝⻟⻢⻥⻦⻨⻩⻬⻮⻰⻳⺕⺆⺁⺄⺅⺉⺋⺖⺙⺜⺝⺣⺤⺦⺩⺪⺭⺳⺷⺸⻀⺫',
                  '月竹足阝阝氵扌艹雨心小辶辶小刀卜牛犭羊老衤角讠钅长门青韦页风飞食饣马鱼鸟麦黄齐齿龙龟彐冂厂乙亻刂卩忄攵日月灬爫丬王疋礻罒羊羊艹罒'))
FUNC = {'了': 'le', '的': 'de', '着': 'zhe', '得': 'de', '都': 'dōu', '还': 'hái', '和': 'hé', '么': 'me', '吗': 'ma', '呢': 'ne', '吧': 'ba', '啊': 'a', '们': 'men', '个': 'gè', '地': 'de', '过': 'guò', '为': 'wèi', '一': 'yī', '不': 'bù', '只': 'zhǐ', '长': 'cháng', '行': 'xíng', '觉': 'jué', '要': 'yào', '会': 'huì', '没': 'méi', '给': 'gěi', '把': 'bǎ', '说': 'shuō', '就': 'jiù', '差': 'chà', '重': 'zhòng', '数': 'shù', '乐': 'lè', '好': 'hǎo', '中': 'zhōng', '那': 'nà', '哪': 'nǎ', '种': 'zhǒng', '少': 'shǎo', '看': 'kàn', '教': 'jiāo', '干': 'gàn', '倒': 'dào', '难': 'nán', '空': 'kōng', '间': 'jiān', '相': 'xiāng', '假': 'jià', '处': 'chù', '得': 'de'}

def syls(py, hz=None):
    out = [s for s in re.split(r"[\s'·-]+", py.lower().strip()) if s]
    if hz and len(out) == len(hz):  # erhua: 儿 read as -r joins the syllable before it (xiàn r → xiànr)
        merged = []
        for c, s_ in zip(hz, out):
            if c == '儿' and s_ == 'r' and merged: merged[-1] += 'r'
            else: merged.append(s_)
        out = merged
    return out

def cite(ch, s):  # write 一 / 不 in citation tone; the app applies sandhi
    if ch == '一' and ''.join(UNMARK.get(c, c) for c in s) == 'yi': return 'yī'
    if ch == '不' and ''.join(UNMARK.get(c, c) for c in s) == 'bu': return 'bù'
    return s

def clean_meanings(ms):
    out = []
    for m in ms:
        if re.match(r'(surname |variant of|old variant|archaic|abbr\. for|see |used in |CL:|Taiwan pr|also pr|erhua variant|\(old\)|\(dialect\))', m, re.I): continue
        m = re.sub(r'\(bound form\)\s*', '', m)
        m = re.sub(r'\[[^\]]*\]', '', m)            # CEDICT pinyin refs
        m = re.sub(r'\|[^\s,;)]*', '', m)             # trad|simp refs
        m = re.sub(r'\s+', ' ', m).strip(' ;,')
        if m and len(m) <= 48 and m not in out: out.append(m)
    return out

# ---------------- words ----------------
raw = json.load(open(os.path.join(RAW, 'complete.json'), encoding='utf-8'))
words, skipped = [], 0
for w in raw:
    lv = sorted(int(l.split('-')[1]) for l in w.get('level', []) if l.startswith('new-'))
    if not lv: continue
    s = w['simplified']
    han = HAN.findall(s)
    if len(han) != len(s): skipped += 1; continue
    f = w['forms'][0]
    py0 = syls(f['transcriptions']['pinyin'])
    if len(py0) != len(han): skipped += 1; continue
    py = [cite(c, p) for c, p in zip(han, py0)]
    py = syls(' '.join(py), han)
    ms = clean_meanings(f['meanings']) or [re.sub(r'\[[^\]]*\]', '', f['meanings'][0]).strip()]
    en = '; '.join(ms[:3])
    if len(en) > 80: en = '; '.join(ms[:2]) if len('; '.join(ms[:2])) <= 80 else ms[0][:80]
    pos = next((POS[p] for p in w.get('pos', []) if p in POS), None)
    cls = [c for c in (f.get('classifiers') or []) if HAN.fullmatch(c)]
    words.append({'s': s, 'py': py, 'en': en, 'pos': pos, 'mw': cls[0] if cls else None, 'lv': lv[0], 'freq': w.get('frequency') or 10**6, 'rad': RADMAP.get(w.get('radical') or '', w.get('radical'))})
print(f'{len(words)} words, {skipped} skipped (pinyin/hanzi mismatch)')

# pinyin for sentences: longest-match over every HSK word, single characters as fallback
WPY = {w['s']: w['py'] for w in words}
CPY = dict(FUNC)
for w in sorted(words, key=lambda w: (len(w['s']), w['freq'])):
    if len(w['py']) == len(w['s']):
        for c, p in zip(w['s'], w['py']): CPY.setdefault(c, p)
MAXW = max(len(k) for k in WPY)
def sent_py(zh):
    out, i, h = [], 0, [c for c in zh if HAN.match(c)]
    text = ''.join(h)
    while i < len(text):
        for L in range(min(MAXW, len(text) - i), 0, -1):
            seg = text[i:i + L]
            if L > 1 and seg in WPY: out += WPY[seg]; i += L; break
            if L == 1:
                if seg not in CPY: return None
                out.append(CPY[seg]); i += 1
    return ' '.join(out)

# ---------------- sentences ----------------
SENT = []
for line in open(os.path.join(RAW, 'cmn.txt'), encoding='utf-8'):
    parts = line.rstrip('\n').split('\t')
    if len(parts) < 3: continue
    en, zh, attr = parts[0].strip(), parts[1].strip().replace(' ', ''), parts[2]
    ids = re.findall(r'#(\d+)', attr)
    if not zh or re.search(r'[A-Za-z0-9０-９Ａ-Ｚａ-ｚ]', zh): continue
    if any(not HAN.match(c) and c not in PUNCT for c in zh): continue
    h = HAN.findall(zh)
    if not 3 <= len(h) <= 24: continue
    SENT.append({'zh': zh, 'en': en, 'h': set(h), 'n': len(h), 'id': ids[-1] if ids else ''})
seen = set(); SENT = [x for x in SENT if not (x['zh'] in seen or seen.add(x['zh']))]
BYCHAR = collections.defaultdict(list)
for i, x in enumerate(SENT):
    for c in x['h']: BYCHAR[c].append(i)
print(f'{len(SENT)} usable sentences')

# ---------------- levels → units ----------------
LEVELS = [(1, 11, 'HSK 1', 'The first 500 words'), (2, 12, 'HSK 2', 'Everyday life'), (3, 13, 'HSK 3', 'Work, study, travel'), (4, 14, 'HSK 4', 'Opinions and stories'),
          (5, 15, 'HSK 5', 'Society and ideas'), (6, 16, 'HSK 6', 'Abstract and formal'), (7, 17, 'HSK 7–9 · I', 'Advanced, most common third'), (8, 18, 'HSK 7–9 · II', 'Advanced, middle third'), (9, 19, 'HSK 7–9 · III', 'Advanced, rarest third')]
bylv = collections.defaultdict(list)
for w in words: bylv[w['lv']].append(w)
band = sorted(bylv.pop(7), key=lambda w: w['freq'])
third = math.ceil(len(band) / 3)
for k in range(3): bylv[7 + k] = band[k * third:(k + 1) * third]
ideal = {1: (4, 10), 2: (4, 12), 3: (5, 14), 4: (5, 16), 5: (6, 18), 6: (6, 20), 7: (6, 22), 8: (6, 22), 9: (6, 22)}
known = set()       # characters met so far, across the whole track
level_chars = set()
used = collections.Counter()
seen_chars = set()
stages, stats = [], collections.Counter()

def pick_sentences(w, allowed, lv, k):
    lo, hi = ideal[lv]
    cands = [SENT[i] for i in BYCHAR.get(w['s'][0], ()) if w['s'] in SENT[i]['zh'] and SENT[i]['h'] <= allowed and lo <= SENT[i]['n'] <= hi and used[SENT[i]['zh']] < 2]
    cands.sort(key=lambda x: (used[x['zh']], abs(x['n'] - (lo + hi) / 2), x['zh']))
    out = []
    for x in cands:
        p = sent_py(x['zh'])
        if not p or len(p.split()) + p.count('r ') + p.endswith('r') * 0 < x['n'] - x['zh'].count('儿') or len(p.split()) > x['n']: continue
        out.append({'zh': x['zh'], 'p': p, 'en': x['en'], 't': x['id']}); used[x['zh']] += 1
        if len(out) == k: break
    return out

for lv, n, title, en in LEVELS:
    ws = sorted(bylv[lv], key=lambda w: w['freq'])
    level_chars |= {c for w in ws for c in w['s']}
    nu = max(1, round(len(ws) / UNIT))
    size = math.ceil(len(ws) / nu)
    units, unitsMeta = [], []
    for ui in range(nu):
        chunk = ws[ui * size:(ui + 1) * size]
        if not chunk: continue
        uid = f'h{lv}u{ui + 1:02d}'
        known |= {c for w in chunk for c in w['s']}
        items, chars = [], {}
        for w in chunk:
            ex = pick_sentences(w, known, lv, 2)
            if len(ex) < 2: ex += [e for e in pick_sentences(w, known | level_chars, lv, 2 - len(ex)) if e['zh'] not in {x['zh'] for x in ex}]
            if not ex: ex = pick_sentences(w, set(CPY), lv, 1)
            stats['ex%d' % min(2, len(ex))] += 1
            it = {'id': f'h{lv}.{w["s"]}', 'k': 'char' if len(w['s']) == 1 else 'word', 's': w['s'], 'p': ' '.join(w['py']), 'en': w['en'], 'hsk': lv if lv <= 6 else 7}
            if w['pos']: it['pos'] = w['pos']
            if w['mw']: it['mw'] = w['mw']
            if ex: it['ex'] = ex
            items.append(it)
            for c, p in (zip(w['s'], w['py']) if len(w['py']) == len(w['s']) else []):
                if c in seen_chars: continue
                seen_chars.add(c)
                single = next((x for x in words if x['s'] == c), None)
                m = single['en'].split(';')[0] if single else f'as in {w["s"]} ({w["en"].split(";")[0]})'
                chars[c] = {'p': (single['py'][0] if single else p), 'm': m[:60], **({'r': single['rad']} if single and single['rad'] else {})}
        # lessons: 8 words each, then drills from the unit's sentences, then a reading of them
        sents = [e for it in items for e in it.get('ex', [])]
        uniq = list({e['zh']: e for e in sents}.values())
        lessons, exs = [], []
        nl = math.ceil(len(items) / 8); cuts = [round(k * len(items) / nl) for k in range(nl + 1)]
        for li in range(nl):
            grp = items[cuts[li]:cuts[li + 1]]
            lessons.append({'id': f'l.{uid}.{li + 1}', 'title': '、'.join(x['s'] for x in grp[:4]) + ('…' if len(grp) > 4 else ''), 'type': 'new', 'items': [x['id'] for x in grp]})
        mid = [e for e in uniq if 5 <= len(HAN.findall(e['zh'])) <= 14]
        random.shuffle(mid)
        for e in mid[:4]: exs.append({'id': f'x.{uid}.o{len(exs)}', 'type': 'order', 'zh': e['zh'], 'p': e['p'], 'en': e['en']})
        for it in random.sample(items, len(items)):
            if sum(1 for x in exs if x['type'] == 'fill') >= 4: break
            e = next((e for e in it.get('ex', []) if it['s'] in e['zh']), None)
            if not e: continue
            others = [x['s'] for x in items if len(x['s']) == len(it['s']) and x['s'] != it['s'] and x['s'] not in e['zh']]
            if len(others) < 3: continue
            o = random.sample(others, 3) + [it['s']]; random.shuffle(o)
            exs.append({'id': f'x.{uid}.f{len(exs)}', 'type': 'fill', 'q': e['zh'].replace(it['s'], '＿＿', 1), 'o': o, 'a': o.index(it['s']), 'en': e['en'], 'why': f'{it["s"]} {it["p"]}: {it["en"]}'})
        for e in [e for e in uniq if e not in mid[:4]][:2]: exs.append({'id': f'x.{uid}.t{len(exs)}', 'type': 'translate', 'en': e['en'], 'a': [e['zh']], 'p': e['p']})
        if exs: lessons.append({'id': f'l.{uid}.d', 'title': '练一练 · Drills', 'type': 'drill', 'ex': [x['id'] for x in exs]})
        texts = []
        if len(uniq) >= 4:
            lines = sorted(uniq, key=lambda e: len(e['zh']))[:10]
            texts.append({'id': f't.{uid}', 'kind': 'reading', 'title': f'读一读 · {title} 第{ui + 1}单元', 'src': 'Example sentences from Tatoeba (CC BY 2.0 FR)', 'lines': [{'zh': e['zh'], 'p': e['p'], 'en': e['en']} for e in lines]})
            lessons.append({'id': f'l.{uid}.r', 'title': '读一读 · Read it all', 'type': 'text', 'text': texts[0]['id']})
        a, b = ui * size + 1, ui * size + len(chunk)
        unit = {'id': uid, 'stage': n, 'n': ui + 1, 'track': 'hsk', 'title': '、'.join(x['s'] for x in chunk[:3]), 'en': f'Words {a}–{b} of {len(ws)}',
                'intro': f'{title}, words {a}–{b}, most common first. The sentences use characters from this unit and earlier ones, so each unit builds on the last. Finish the lessons, then pass the checkpoint (85%) to open the next unit.',
                'items': items, 'chars': chars, 'texts': texts, 'exercises': exs, 'lessons': lessons}
        units.append(unit)
        unitsMeta.append({'id': uid, 'n': ui + 1, 'title': unit['title'], 'en': unit['en'], 'lessons': [l['id'] for l in lessons]})
    os.makedirs(os.path.join(DATA, 'hsk'), exist_ok=True)
    json.dump({'stage': n, 'level': lv, 'units': units}, open(os.path.join(DATA, 'hsk', f'hsk{lv}.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    stages.append({'n': n, 'track': 'hsk', 'title': title, 'en': f'{en} · {len(ws)} words', 'pack': f'hsk/hsk{lv}.json', 'units': [], 'unitsMeta': unitsMeta})
    print(f'{title}: {len(ws)} words, {len(units)} units, {sum(len(u["exercises"]) for u in units)} drills')

idx = json.load(open(os.path.join(DATA, 'index.json'), encoding='utf-8'))
idx['stages'] = [s for s in idx['stages'] if s.get('track') != 'hsk'] + stages
json.dump(idx, open(os.path.join(DATA, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('examples per word:', dict(stats))
