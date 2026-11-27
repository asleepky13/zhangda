"""Build the whole course from the lesson plans plus open data.

Part 1  部首  data/p1/uNN.json   from course/tab1.md (radical notes, Unit 0) + course/bank.md (P1-U01.. practice data)
Part 2  HSK   data/hsk/hskN.json from course/hsk.md (2025 syllabus progression, unit themes, grammar, units 1-5 written out),
              course/bank.md (HSK1-U01..05 practice data) and tools/raw (2025 word lists, Tatoeba sentences)
Every unit: lessons of new items, a drills lesson, a reading; review tests every 4 (Part 1) / 5 (HSK) units.
Run: python -I tools/build_course.py      (then node tools/validate.cjs, python -I tools/make_audio.py [--hsk N])
"""
import json, os, re, sys, csv, io, math, random, collections
sys.stdout.reconfigure(encoding='utf-8'); random.seed(11)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, DATA, PLAN = os.path.join(ROOT, 'tools', 'raw'), os.path.join(ROOT, 'data'), os.path.join(ROOT, 'course')
HAN = re.compile(r'[㐀-鿿]')
PUNCT = set('，。！？、：；“”‘’（）《》…—·「」『』')
TONES = {'a': 'āáǎà', 'e': 'ēéěè', 'i': 'īíǐì', 'o': 'ōóǒò', 'u': 'ūúǔù', 'ü': 'ǖǘǚǜ'}
UNMARK = {c: v for v, s in TONES.items() for c in s}
POS = {'n': 'n', 'nr': 'n', 'ns': 'n', 'nt': 'n', 'nz': 'n', 'nw': 'n', 't': 'n', 's': 'n', 'f': 'n', 'j': 'n', 'v': 'v', 'vn': 'v', 'vd': 'v', 'a': 'adj', 'ad': 'adj', 'an': 'adj', 'b': 'adj', 'z': 'adj',
       'd': 'adv', 'r': 'pron', 'm': 'num', 'mq': 'num', 'q': 'mw', 'p': 'prep', 'c': 'conj', 'u': 'part', 'y': 'part', 'k': 'part', 'e': 'interj', 'o': 'interj', 'i': 'phrase', 'l': 'phrase', 'h': 'prefix'}
FUNC = {'了': 'le', '的': 'de', '着': 'zhe', '得': 'de', '都': 'dōu', '还': 'hái', '和': 'hé', '么': 'me', '吗': 'ma', '呢': 'ne', '吧': 'ba', '啊': 'a', '们': 'men', '个': 'gè', '地': 'de', '过': 'guò', '为': 'wèi', '一': 'yī', '不': 'bù', '只': 'zhǐ', '长': 'cháng', '行': 'xíng', '觉': 'jué', '要': 'yào', '会': 'huì', '没': 'méi', '给': 'gěi', '把': 'bǎ', '说': 'shuō', '就': 'jiù', '差': 'chà', '重': 'zhòng', '数': 'shù', '乐': 'lè', '好': 'hǎo', '中': 'zhōng', '那': 'nà', '哪': 'nǎ', '种': 'zhǒng', '少': 'shǎo', '看': 'kàn', '教': 'jiāo', '干': 'gàn', '倒': 'dào', '难': 'nán', '空': 'kōng', '间': 'jiān', '相': 'xiāng', '假': 'jià', '处': 'chù', '便': 'biàn'}
PY_OVERRIDE = {'不了': ['bù', 'liǎo'], '便宜': ['pián', 'yi'], '王明': ['wáng', 'míng'], '李月': ['lǐ', 'yuè'], '大卫': ['dà', 'wèi']}

def syls(py, hz=None):
    out = [s for s in re.split(r"[\s'·-]+", py.lower().strip()) if s]
    if hz and len(out) == len(hz):
        merged = []
        for c, s_ in zip(hz, out):
            if c == '儿' and s_ == 'r' and merged: merged[-1] += 'r'
            else: merged.append(s_)
        out = merged
    return out

def cite(ch, s):
    base = ''.join(UNMARK.get(c, c) for c in s)
    return 'yī' if ch == '一' and base == 'yi' else 'bù' if ch == '不' and base == 'bu' else s

def clean_meanings(ms):
    out = []
    for m in ms:
        if re.match(r'(surname |variant of|old variant|archaic|abbr\. for|see |used in |CL:|Taiwan pr|also pr|erhua variant|\(old\)|\(dialect\))', m, re.I): continue
        m = re.sub(r'\(bound form\)\s*', '', m); m = re.sub(r'\[[^\]]*\]', '', m); m = re.sub(r'\|[^\s,;)]*', '', m)
        m = re.sub(r'\s+', ' ', m).strip(' ;,')
        if m and len(m) <= 48 and m not in out: out.append(m)
    return out

# ---------------- dictionary (2025 HSK 3.0 lists) ----------------
raw = json.load(open(os.path.join(RAW, 'complete.json'), encoding='utf-8'))
WORDS = {}
for w in raw:
    lv = sorted(int(l.split('-')[1]) for l in w.get('level', []) if l.startswith('newest-'))
    s = w['simplified']; han = HAN.findall(s)
    if len(han) != len(s): continue
    f = w['forms'][0]; py0 = syls(f['transcriptions']['pinyin'])
    if len(py0) != len(han): continue
    py = syls(' '.join(cite(c, p) for c, p in zip(han, py0)), han)
    ms = clean_meanings(f['meanings']) or [re.sub(r'\[[^\]]*\]', '', f['meanings'][0]).strip()]
    en = '; '.join(ms[:3]); en = en if len(en) <= 80 else ms[0][:80]
    cls = [c for c in (f.get('classifiers') or []) if HAN.fullmatch(c)]
    WORDS[s] = {'s': s, 'py': py, 'en': en, 'pos': next((POS[p] for p in w.get('pos', []) if p in POS), None), 'mw': cls[0] if cls else None,
                'lv': lv[0] if lv else None, 'freq': w.get('frequency') or 10**6}
WPY = {k: v['py'] for k, v in WORDS.items()}; WPY.update(PY_OVERRIDE)
CPY = dict(FUNC)
for w in sorted(WORDS.values(), key=lambda w: (len(w['s']), w['freq'])):
    if len(w['py']) == len(w['s']):
        for c, p in zip(w['s'], w['py']): CPY.setdefault(c, p)
MAXW = max(len(k) for k in WPY)
def pinyin(zh):
    text = ''.join(HAN.findall(zh)); out, i = [], 0
    while i < len(text):
        for L in range(min(MAXW, len(text) - i), 0, -1):
            seg = text[i:i + L]
            if L > 1 and seg in WPY: out += WPY[seg]; i += L; break
            if L == 1:
                if seg not in CPY: return None
                out.append(CPY[seg]); i += 1
    return ' '.join(out)

# ---------------- Tatoeba sentences ----------------
SENT = []
for line in open(os.path.join(RAW, 'cmn.txt'), encoding='utf-8'):
    parts = line.rstrip('\n').split('\t')
    if len(parts) < 3: continue
    en, zh = parts[0].strip(), parts[1].strip().replace(' ', '')
    if not zh or re.search(r'[A-Za-z0-9０-９Ａ-Ｚａ-ｚ]', zh) or any(not HAN.match(c) and c not in PUNCT for c in zh): continue
    h = HAN.findall(zh)
    if 3 <= len(h) <= 24: SENT.append({'zh': zh, 'en': en, 'h': set(h), 'n': len(h)})
seen = set(); SENT = [x for x in SENT if not (x['zh'] in seen or seen.add(x['zh']))]
BYCHAR = collections.defaultdict(list)
for i, x in enumerate(SENT):
    for c in x['h']: BYCHAR[c].append(i)
used = collections.Counter()
def tatoeba(word, allowed, lo, hi, k):
    cands = [SENT[i] for i in BYCHAR.get(word[0], ()) if word in SENT[i]['zh'] and SENT[i]['h'] <= allowed and lo <= SENT[i]['n'] <= hi and used[SENT[i]['zh']] < 2]
    cands.sort(key=lambda x: (used[x['zh']], abs(x['n'] - (lo + hi) / 2), x['zh']))
    out = []
    for x in cands:
        p = pinyin(x['zh'])
        if not p: continue
        out.append({'zh': x['zh'], 'p': p, 'en': x['en']}); used[x['zh']] += 1
        if len(out) == k: break
    return out

# ---------------- markdown helpers ----------------
def md_html(md):  # tables, bold, italics, numbered/bulleted lists, paragraphs: enough for the plans
    esc = lambda t: t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    inline = lambda t: re.sub(r'\*([^*]+)\*', r'<i>\1</i>', re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', esc(t))).replace('\\_', '_')
    out, rows, lst = [], [], None
    def flush():
        nonlocal rows, lst
        if rows:
            head, body = rows[0], [r for r in rows[1:] if not re.fullmatch(r'[\s|:-]+', '|'.join(r))]
            out.append('<div class="tblw"><table><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body) + '</table></div>')
            rows = []
        if lst: out.append(f'<{lst[0]}>' + ''.join(f'<li>{inline(x)}</li>' for x in lst[1]) + f'</{lst[0]}>'); lst = None
    for line in md.split('\n'):
        t = line.strip()
        if t.startswith('|'): rows.append([c.strip() for c in t.strip('|').split('|')]); continue
        m = re.match(r'(\d+)\.\s+(.*)', t) or re.match(r'[-*]\s+(.*)', t)
        if m:
            kind = 'ol' if t[0].isdigit() else 'ul'
            if rows: flush()
            if not lst or lst[0] != kind: flush(); lst = (kind, [])
            lst[1].append(m.group(m.lastindex)); continue
        flush()
        if t: out.append(f'<p>{inline(t)}</p>')
    flush()
    return '\n'.join(out)

def sections(md, pat):
    heads = [(m.start(), m.group(0)) for m in re.finditer(pat, md, re.M)]
    return [(h, md[a + len(h):(heads[i + 1][0] if i + 1 < len(heads) else len(md))]) for i, (a, h) in enumerate(heads)]

def fenced(body):
    return [m.group(2) for m in re.finditer(r'```(csv|text)\n(.*?)```', body, re.S)]

def parse_bank_unit(body):
    blocks = fenced(body)
    items = list(csv.DictReader(io.StringIO(blocks[0])))
    sents = list(csv.DictReader(io.StringIO(blocks[1])))
    auth = list(csv.DictReader(io.StringIO(blocks[2])))
    reading = blocks[3].strip()
    rq = list(csv.DictReader(io.StringIO(blocks[4])))
    return items, sents, auth, reading, rq

def split_lines(text):
    t = text.replace('\n', '')  # keep a closing quote with its sentence
    parts = re.findall(r'[^。！？]*[。！？][”’」』]*', t)
    rest = t[sum(len(x) for x in parts):]
    return [x for x in parts + [rest] if x.strip()]

def sent_obj(zh, en):
    p = pinyin(zh)
    if not p: print('  no pinyin for', zh); return None
    return {'zh': zh, 'p': p, 'en': en}

def unit_from_bank(uid, track, stage, n, title, en, intro, body, item_id, extra_lessons=(), notes=None, review=None):
    items_raw, sents_raw, auth, reading, rq = parse_bank_unit(body)
    sents = []
    for s in sents_raw:
        zh = ''.join(s['tokens'].split())
        o = sent_obj(zh, s['en'])
        if o: o['tok'] = [t for t in s['tokens'].split() if not all(c in PUNCT for c in t)]; o['tg'] = s['targets'].split(); sents.append(o)
    items, chars = [], {}
    for r in items_raw:
        zh = r['zh']; single = len(zh) == 1
        p = r['py'].split('/')[0].strip() if single else pinyin(zh) or r['py']
        words = [[x.split('/')[0].strip(), x.split('/')[1].strip(), x.split('/')[2].strip()] for x in r['words'].split(';') if x.count('/') >= 2]
        ex = [{k: e[k] for k in ('zh', 'p', 'en')} for e in sents if zh in e['zh']][:3]
        it = {'id': item_id(zh), 'k': 'char' if single else 'word', 's': zh, 'p': p, 'en': r['en']}
        if r['radical'] and r['radical'] != '—': it['rad'] = r['radical'].split(' ')[0]
        if single and r['component'] not in ('—', ''): it['comp'] = r['component']
        if words: it['words'] = words
        if r['lookalikes']: it['look'] = r['lookalikes'].split()
        if ex: it['ex'] = ex
        w = WORDS.get(zh)
        if w and w['pos']: it['pos'] = w['pos']
        items.append(it)
        if single:
            chars[zh] = {'p': p, 'm': r['en'], **({'r': it['rad']} if it.get('rad') else {}), **({'c': [it['rad'], it['comp']]} if it.get('rad') and it.get('comp') and it['comp'] != it['rad'] else {})}
            if notes and zh in notes: chars[zh]['h'] = notes[zh]
    exs = []
    for a in auth:
        if a['type'] == 'error': exs.append({'id': a['id'], 'type': 'error', 'q': a['prompt'], 'ans': a['answer'], 'why': a['note']})
        else:
            o = [x.strip() for x in a['options'].split(' / ')]
            exs.append({'id': a['id'], 'type': 'dialogue', 'q': a['prompt'], 'o': o, 'a': o.index(a['answer'].strip()) if a['answer'].strip() in o else 0})
    for e in [e for e in sents if 5 <= len(HAN.findall(e['zh'])) <= 14][:4]:
        exs.append({'id': f'x.{uid}.o{len(exs)}', 'type': 'order', 'zh': e['zh'], 'p': e['p'], 'en': e['en']})
    lines = [sent_obj(x, '') for x in split_lines(reading)]
    text = {'id': f't.{uid}', 'kind': 'reading', 'title': f'读一读 · {title}', 'src': 'Original reading', 'noTr': True,
            'lines': [l for l in lines if l], 'qs': [{'q': q['question'], 'o': [x.strip() for x in q['options'].split(' / ')], 'a': [x.strip() for x in q['options'].split(' / ')].index(q['answer'].strip())} for q in rq]}
    per = 4 if track == 'p1' else 7
    lessons = list(extra_lessons)
    nl = math.ceil(len(items) / per)
    for li in range(nl):
        grp = items[li * len(items) // nl:(li + 1) * len(items) // nl]
        lessons.append({'id': f'l.{uid}.{li + 1}', 'title': '、'.join(x['s'] for x in grp), 'type': 'new', 'items': [x['id'] for x in grp]})
    lessons.append({'id': f'l.{uid}.d', 'title': '练一练 · Errors, dialogues, word order', 'type': 'drill', 'ex': [x['id'] for x in exs]})
    lessons.append({'id': f'l.{uid}.r', 'title': '读一读 · Reading', 'type': 'text', 'text': text['id']})
    if review: lessons.append(review)
    return {'id': uid, 'stage': stage, 'n': n, 'track': track, 'title': title, 'en': en, 'intro': intro, 'items': items, 'chars': chars, 'texts': [text],
            'exercises': exs, 'lessons': lessons, 'sents': [{k: e[k] for k in ('zh', 'p', 'en', 'tok', 'tg')} for e in sents]}

bank = open(os.path.join(PLAN, 'bank.md'), encoding='utf-8').read()
BANK = {h.split()[1]: b for h, b in sections(bank, r'^## (P1-U\d+|HSK\d-U\d+).*$')}

# ================= Part 1 =================
tab1 = open(os.path.join(PLAN, 'tab1.md'), encoding='utf-8').read()
T1 = {}
for h, b in sections(tab1, r'^## .*$'):
    m = re.match(r'## Unit (\d+): (.*)', h)
    if m: T1[int(m.group(1))] = (m.group(2).strip(), b)
p1_units, p1_known = [], set()
unit0 = md_html(T1[0][1].split('**Exercise.**')[0])
for k in range(1, 18):
    title, body = T1[k]
    note = body.split('**Characters**')[0].strip()
    notes = {}
    for row in re.findall(r'^\| (\S) \| [^|]+\| [^|]+\| ([^|]+)\|', body, re.M):
        notes[row[0]] = row[1].strip()
    extra = [{'id': 'l.p1u00.0', 'title': '字的结构 · How characters are built', 'type': 'info', 'html': unit0}] if k == 1 else []
    extra.append({'id': f'l.p1u{k:02d}.0', 'title': f'部首 · {title}', 'type': 'info', 'html': f'<p class="muted center">部首 · Radical</p><h2 class="display" style="text-align:center">{title}</h2>' + md_html(note)})
    review = None
    if k % 4 == 0 or k == 17:
        span = list(range(k - 3, k + 1)) if k % 4 == 0 else list(range(1, 18))
        review = {'id': f'l.p1u{k:02d}.t', 'title': 'Final test · Units 1–17' if k == 17 else f'Review test · Units {span[0]}–{span[-1]}', 'type': 'review', 'units': [f'p1u{x:02d}' for x in span], 'n': 60 if k == 17 else 40}
    u = unit_from_bank(f'p1u{k:02d}', 'p1', 1, k, title, f'Unit {k}', md_html(note), BANK[f'P1-U{k:02d}'], lambda zh: 'c.' + zh, extra, notes, review)
    p1_known |= {c for it in u['items'] for c in it['s']} | {c for s in u['sents'] for c in HAN.findall(s['zh'])}
    os.makedirs(os.path.join(DATA, 'p1'), exist_ok=True)
    json.dump(u, open(os.path.join(DATA, 'p1', f'u{k:02d}.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    p1_units.append(f'p1/u{k:02d}.json')
print(f'Part 1: {len(p1_units)} units')

# ================= Part 2: HSK on the 2025 syllabus =================
hsk = open(os.path.join(PLAN, 'hsk.md'), encoding='utf-8').read()
MAP = {}   # unit number → (level, theme, focus)
for m in re.finditer(r'^\| (\d+) \| HSK (\d) \| ([^|]+)\| ([^|]+)\|', hsk, re.M): MAP[int(m.group(1))] = (int(m.group(2)), m.group(3).strip(), m.group(4).strip())
for m in re.finditer(r'^\| (\d+)–(\d+) \| HSK (\d) \| ([^|]+)\| ([^|]+)\|', hsk, re.M):
    for n in range(int(m.group(1)), int(m.group(2)) + 1): MAP[n] = (int(m.group(3)), m.group(4).strip(), m.group(5).strip())
for m in re.finditer(r'^\| (\d+)–(\d+) \| ([^|]+)\| ([^|]+)\|', hsk, re.M):
    if int(m.group(1)) >= 133:
        for n in range(int(m.group(1)), int(m.group(2)) + 1): MAP[n] = (7, m.group(3).strip(), m.group(4).strip())
WRITTEN = {}
for h, b in sections(hsk, r'^## HSK 1 Unit (\d+): .*$'):
    n = int(re.match(r'## HSK 1 Unit (\d+)', h).group(1))
    gram = re.search(r'\*\*Grammar\*\*(.*?)\*\*Dialogue', b, re.S).group(1)
    dia = re.findall(r'^([AB]): (.+?) \*(.+?)\*\s*$', b, re.M)
    WRITTEN[n] = {'goal': re.search(r'Goal: (.*)', b).group(1).strip(), 'grammar': md_html(gram.strip()), 'dialogue': dia, 'title': h.split(': ', 1)[1].strip()}
LEVELS = [(1, 11, 'HSK 1', 15), (2, 12, 'HSK 2', 10), (3, 13, 'HSK 3', 20), (4, 14, 'HSK 4', 25), (5, 15, 'HSK 5', 32), (6, 16, 'HSK 6', 30), (7, 17, 'HSK 7–9', 56)]
THEME = {  # English keywords that pull a level's words into a themed unit (the rest go in frequency order)
 'Greetings': 'hello|name|thank|sorry|goodbye|teacher|student', 'Numbers': r'\bnumber|zero|hundred|thousand|how many|years old|measure', 'Family': 'father|mother|brother|sister|son|daughter|child|family|friend|husband|wife|grand',
 'Time': r'today|tomorrow|yesterday|year|month|week|o.clock|minute|hour|morning|noon|afternoon|evening|night|birthday|time|now', 'Places': 'school|hospital|shop|store|restaurant|station|airport|park|room|home|inside|front|behind|place|where',
 'Food': r'eat|drink|rice|tea|water|food|meal|apple|vegetable|fruit|coffee|milk|egg|noodle|dish|hungry|cup|bowl|meat|fish|bread|chicken', 'Shopping': r'buy|sell|money|yuan|price|cheap|expensive|shop|pay|clothes|kuai|dollar',
 'Daily routine': r'sleep|get up|wash|work|class|go to|bath|morning|breakfast|lunch|dinner|every day|busy', 'School': r'study|learn|school|class|lesson|exam|book|read|write|word|character|homework|know|understand|question|teacher',
 'Getting around': r'car|bus|taxi|train|plane|bike|subway|ride|drive|road|ticket|walk|airport|station|from|to go', 'Weather': r'weather|rain|snow|wind|cold|hot|warm|cool|sun|cloud|sky|temperature',
 'Health': r'ill|sick|doctor|hospital|medicine|body|hurt|pain|tired|happy|sad|feel|cold \(|healthy|eye|head', 'Hobbies': r'sing|song|dance|movie|film|music|play|sport|ball|game|swim|run|book|photo|draw|travel|TV|watch',
 'Asking': r'who|why|how|what|which|where|question|answer|ask', 'Linking': r'because|so|but|still|already|can|may|and|also|then|if', 'Directions': r'left|right|east|west|south|north|straight|turn|far|near|side|direction|corner',
 'Comparisons': r'than|more|most|same|different|compare|tall|short|big|small|long|fast|slow', 'Experiences': r'ever|time \(|once|never|experience|travel|visit|abroad', 'Clothes': r'clothes|shirt|trousers|skirt|shoe|hat|wear|color|colour|red|blue|white|black|green|yellow',
 'Work': r'work|job|company|office|boss|colleague|meeting|business|salary|manager', 'Nature': r'mountain|river|lake|sea|tree|flower|grass|animal|bird|environment|nature|forest',
 'Travel': r'travel|trip|hotel|passport|visa|tour|culture|museum|country|city|ticket', 'Opinions': r'think|believe|opinion|agree|seem|certainly|view|feel|suggest',
 'Relationships': r'love|friend|relationship|marry|marriage|feeling|emotion|angry|happy|sad|miss|trust', 'careers': r'job|career|work|company|interview|resume|salary|boss|colleague|employ',
 'Services': r'bank|hospital|rent|apartment|doctor|account|card|service|repair|landlord', 'Education': r'school|education|student|university|exam|study|learn|knowledge|degree|course',
 'Media': r'news|newspaper|internet|computer|phone|online|media|television|technology|software|network|data', 'Economy': r'economy|market|price|money|consumer|buy|sell|trade|bank|finance|cost|income',
 'science': r'health|science|environment|research|disease|medical|pollution|energy|climate|experiment', 'History': r'history|tradition|ancient|dynasty|festival|culture|custom|idiom|poem|poetry',
 'Arguing': r'argue|reason|prove|therefore|in short|conclusion|evidence|opinion|point', 'law': r'law|society|social|court|government|policy|public|crime|right|citizen',
 'Psychology': r'psycholog|behavio|mind|emotion|attitude|habit|personality|motiv|anxious|confiden', 'management': r'business|manage|company|market|report|plan|product|customer|strategy|project',
 'Literature': r'literature|novel|poem|poet|writer|author|story|character|classical|essay', 'News': r'news|report|speech|announce|public|press|headline|media',
 'humanities': r'history|philosophy|culture|thought|theory|lecture|essay|argument|scholar', 'technology': r'science|technology|internet|computer|digital|artificial|machine|data|research|engineer',
 'Economics': r'economy|economic|finance|financial|market|invest|company|profit|stock|bank|trade', 'Politics': r'politic|law|government|international|policy|official|state|nation|diplomat|legal',
 'Medicine': r'medic|health|disease|patient|doctor|hospital|treatment|virus|symptom|drug', 'Classical': r'ancient|classical|poem|poetry|Confucius|literary|dynasty|scholar',
 'arts': r'art|film|music|literature|novel|painting|performance|criticism|artist|story', 'Professional': r'proposal|letter|formal|debate|interpret|translate|negotiate|presentation|contract'}
def theme_re(theme):
    for k, v in THEME.items():
        if k.lower() in theme.lower(): return re.compile(v, re.I)
    return None

stages, pk_known = [], set(p1_known)
taken = set()

# HSK 2-3 written out (course/hsk2.md → units 16-25, hsk3.md → 26-45): words, grammar, dialogue, activities, question bank
W2 = {}
def _rows(t):
    out = [[c.strip() for c in r.strip().strip('|').split('|')] for r in t.split('\n') if r.strip().startswith('|') and not re.fullmatch(r'[\s|:-]+', r.strip())]
    return out[1:]
for fname, tag, off in (('hsk2.md', 'H2', 15), ('hsk3.md', 'H3', 25)):
  for h, b in sections(open(os.path.join(PLAN, fname), encoding='utf-8').read(), rf'^## {tag}-U(\d+): .*$'):
    k = int(re.match(rf'## {tag}-U(\d+)', h).group(1)); part = sections(b, r'^### .*$')
    get = lambda name: next((v for kk, v in part if kk.startswith('### ' + name)), '')
    W2[off + k] = {'title': h.split(': ', 1)[1].strip(), 'goal': (re.search(r'Goal: (.*)', b) or [None, ''])[1].strip(), 'words': _rows(get('Words')), 'grammar': md_html(get('Grammar').strip()),
                  'dialogue': re.findall(r'^([AB]): (.+?) \*(.+?)\*\s*$', get('Dialogue'), re.M), 'acts': md_html(get('Practice activities').strip()), 'qs': _rows(get('Question bank'))}
reserved = {r[1] for w in W2.values() for r in w['words']}
alts = lambda t: [x.strip() for x in t.split('‖') if x.strip()]
def unit_written2(uid, N, lv, stage, title, review):
    W = W2[N]; items, chars, exs = [], {}, []
    sents = []
    for r in W['qs']:
        if r[1] == 'translate':
            o = sent_obj(alts(r[3])[0], r[2])
            if o and '…' not in o['zh']: sents.append(o)
    for _, zh, en in W['dialogue']:
        o = sent_obj(zh, en)
        if o: sents.append(o)
    words = [r for r in W['words'] if r[1] not in taken]
    again = [r for r in W['words'] if r[1] in taken]  # the plan reuses earlier words on purpose: listed, not re-taught
    for r in words:
        zh = r[1]; w = WORDS.get(zh)
        py = pinyin(zh) or (' '.join(w['py']) if w else r[2])
        it = {'id': f'k{lv}.{zh}', 'k': 'char' if len(zh) == 1 else 'word', 's': zh, 'p': py, 'en': r[3]}
        if w and w['pos']: it['pos'] = w['pos']
        if w and w['mw']: it['mw'] = w['mw']
        ex = [{k_: e[k_] for k_ in ('zh', 'p', 'en')} for e in sents if zh in e['zh']][:2]
        if len(ex) < 2: ex += tatoeba(zh, pk_known | {c for x in words for c in x[1]}, 4, 14, 2 - len(ex))
        if ex: it['ex'] = ex
        parts = [re.sub(r'\s*\(.*?\)', '', x).strip() for x in r[4].split('+')] if len(zh) == 1 and '+' in r[4] and ';' not in r[4] else []
        if parts:
            it['rad'] = parts[0]; it['comp'] = parts[-1]
            chars[zh] = {'p': py, 'm': r[3], 'r': parts[0], 'c': parts}
        items.append(it); taken.add(zh)
    unit_words = [it['s'] for it in items]
    fills = [r for r in W['qs'] if r[1] == 'fill']
    for r in W['qs']:
        qid, T, prompt, ans = r[0], r[1], r[2], r[3]
        if T == 'fill':
            hint = (re.search(r'\(([^)]*)\)\s*$', prompt) or [None, ''])[1]
            q = re.sub(r'\s*\([^)]*\)\s*$', '', prompt).replace('（ ）', '＿＿').replace('（）', '＿＿')
            pool = [f[3] for f in fills if f[3] != ans and len(f[3]) == len(ans)] + [wd for wd in unit_words if len(wd) == len(ans)]
            pool = [x for x in dict.fromkeys(pool) if x != ans and x not in q]
            o = random.sample(pool, min(3, len(pool))) + [ans]; random.shuffle(o)
            exs.append({'id': qid, 'type': 'fill', 'q': q, 'o': o, 'a': o.index(ans), **({'en': hint} if hint else {})})
        elif T == 'order':
            exs.append({'id': qid, 'type': 'order2', 'tok': [t.strip() for t in prompt.split('/')], 'a': alts(ans)})
        elif T == 'mcq':
            m = re.split(r'\s*([A-D])\)\s*', prompt); q = m[0].strip(); opts = [m[i + 1].strip() for i in range(1, len(m) - 1, 2)]
            exs.append({'id': qid, 'type': 'mcq', 'q': q.strip('"“”'), 'o': opts, 'a': 'ABCD'.index(ans.strip()[0])})
        elif T == 'translate': exs.append({'id': qid, 'type': 'translate', 'en': prompt, 'a': alts(ans)})
        elif T == 'fix': exs.append({'id': qid, 'type': 'error', 'q': prompt, 'ans': alts(ans)[0], 'alts': alts(ans)})
        elif T == 'speak': exs.append({'id': qid, 'type': 'speak', 'en': prompt, 'a': alts(ans)})
        elif T == 'reply': exs.append({'id': qid, 'type': 'reply', 'q': prompt, 'a': alts(ans)})
    lessons = [{'id': f'l.{uid}.0', 'title': '语法 · Grammar', 'type': 'info', 'html': f'<p class="muted center">语法 · Grammar</p><h2 class="display" style="text-align:center">{W["title"]}</h2><p class="muted">{W["goal"]}</p>' + W['grammar'] + (f'<h3>Words from earlier units</h3><div class="tblw"><table>' + ''.join(f'<tr><td class="hz">{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>' for r in again) + '</table></div>' if again else '') + '<h3>Practice activities</h3>' + W['acts']}]
    nl = math.ceil(len(items) / 7)
    for li in range(nl):
        grp = items[li * len(items) // nl:(li + 1) * len(items) // nl]
        lessons.append({'id': f'l.{uid}.{li + 1}', 'title': '、'.join(x['s'] for x in grp[:4]) + ('…' if len(grp) > 4 else ''), 'type': 'new', 'items': [x['id'] for x in grp]})
    texts = [{'id': f't.{uid}.dia', 'kind': 'dialogue', 'title': f'对话 · {W["title"]}', 'src': 'Read aloud, copy by hand, then rewrite it from the English', 'lines': [o for o in (sent_obj(zh, en) for _, zh, en in W['dialogue']) if o]}]
    lessons.append({'id': f'l.{uid}.dia', 'title': '对话 · Dialogue', 'type': 'text', 'text': texts[0]['id']})
    first = [x for x in exs if x['type'] in ('fill', 'order2', 'mcq')]; second = [x for x in exs if x not in first]
    lessons.append({'id': f'l.{uid}.d', 'title': '练一练 · Fill, order, choose', 'type': 'drill', 'ex': [x['id'] for x in first]})
    lessons.append({'id': f'l.{uid}.e', 'title': '练一练 · Translate, fix, speak, reply', 'type': 'drill', 'ex': [x['id'] for x in second]})
    if review: lessons.append(review)
    return {'id': uid, 'stage': stage, 'n': N, 'track': 'hsk', 'title': W['title'], 'en': f'{title} · Unit {N}', 'intro': f'<p>{W["goal"]}</p>', 'items': items, 'chars': chars, 'texts': texts, 'exercises': exs, 'lessons': lessons,
            'sents': [{**e, 'tg': [w for w in unit_words if w in e['zh']]} for e in sents]}
unit_no = 0
for lv, stage, title, nunits in LEVELS:
    pool = sorted([w for w in WORDS.values() if w['lv'] == lv], key=lambda w: w['freq'])
    lv_chars = {c for w in pool for c in w['s']}
    first = unit_no + 1
    units, meta = [], []
    for k in range(nunits):
        unit_no += 1; N = unit_no
        theme, focus = MAP[N][1], MAP[N][2]
        uid = f'k{N:03d}'
        review = None
        if N % 5 == 0 or k == nunits - 1:
            a = max(first, N - 4)
            review = {'id': f'l.{uid}.t', 'title': f'Review test · Units {a}–{N}', 'type': 'review', 'units': [f'k{x:03d}' for x in range(a, N + 1)], 'n': 40}
        if N in WRITTEN:  # units 1-5: the written plan + practice bank
            W = WRITTEN[N]
            gram = {'id': f'l.{uid}.0', 'title': f'语法 · Grammar', 'type': 'info', 'html': f'<p class="muted center">语法 · Grammar</p><h2 class="display" style="text-align:center">{W["title"]}</h2><p class="muted">{W["goal"]}</p>' + W['grammar']}
            u = unit_from_bank(uid, 'hsk', stage, N, W['title'], f'{title} · Unit {N}', f'<p>{W["goal"]}</p>', BANK[f'HSK1-U{N:02d}'], lambda zh: f'k{lv}.{zh}', [gram], None, review)
            dl = [o for o in (sent_obj(zh, en) for _, zh, en in W['dialogue']) if o]
            u['texts'].append({'id': f't.{uid}.dia', 'kind': 'dialogue', 'title': f'对话 · {W["title"]}', 'src': 'Read aloud, copy by hand, then rewrite it from the English', 'lines': dl})
            u['lessons'].insert(len(u['lessons']) - (2 if review else 1), {'id': f'l.{uid}.dia', 'title': '对话 · Dialogue', 'type': 'text', 'text': f't.{uid}.dia'})
            for it in u['items']:
                w = WORDS.get(it['s'])
                if w and w['mw']: it['mw'] = w['mw']
                taken.add(it['s'])
            pk_known |= {c for it in u['items'] for c in it['s']}
        elif N in W2:  # HSK 2-3 units 16-45: the written plans
            u = unit_written2(uid, N, lv, stage, title, review)
            pk_known |= {c for it in u['items'] for c in it['s']}
        else:
            size = math.ceil(len([w for w in pool if w['s'] not in taken and w['s'] not in reserved]) / max(1, nunits - k))
            rest = [w for w in pool if w['s'] not in taken and w['s'] not in reserved]
            focus_words = [t for t in re.findall(r'[㐀-鿿]+', focus) if t in WORDS and t not in taken and t not in reserved]
            rx = theme_re(theme)
            themed = [w for w in rest if rx and rx.search(w['en'])] if rx else []
            pick, seenw = [], set()
            for w in [WORDS[t] for t in focus_words] + themed[:size // 2] + rest:
                if w['s'] in seenw or w['s'] in taken or w['s'] in reserved: continue
                pick.append(w); seenw.add(w['s'])
                if len(pick) >= size: break
            pick.sort(key=lambda w: w['freq'])
            for w in pick: taken.add(w['s'])
            pk_known |= {c for w in pick for c in w['s']}
            lo, hi = (4, 12) if lv <= 2 else (5, 16) if lv <= 4 else (6, 22)
            items = []
            for w in pick:
                ex = tatoeba(w['s'], pk_known, lo, hi, 2)
                if len(ex) < 2: ex += [e for e in tatoeba(w['s'], pk_known | lv_chars, lo, hi, 2 - len(ex)) if e['zh'] not in {x['zh'] for x in ex}]
                it = {'id': f'k{lv}.{w["s"]}', 'k': 'char' if len(w['s']) == 1 else 'word', 's': w['s'], 'p': ' '.join(w['py']), 'en': w['en']}
                for f_ in ('pos', 'mw'):
                    if w[f_]: it[f_] = w[f_]
                if ex: it['ex'] = ex
                items.append(it)
            sents = list({e['zh']: e for it in items for e in it.get('ex', [])}.values())
            exs = []
            for e in [e for e in sents if 5 <= len(HAN.findall(e['zh'])) <= 14][:4]: exs.append({'id': f'x.{uid}.o{len(exs)}', 'type': 'order', 'zh': e['zh'], 'p': e['p'], 'en': e['en']})
            for it in random.sample(items, len(items)):
                if sum(x['type'] == 'fill' for x in exs) >= 4: break
                e = next((e for e in it.get('ex', []) if it['s'] in e['zh']), None)
                others = [x['s'] for x in items if len(x['s']) == len(it['s']) and x['s'] != it['s'] and e and x['s'] not in e['zh']]
                if not e or len(others) < 3: continue
                o = random.sample(others, 3) + [it['s']]; random.shuffle(o)
                exs.append({'id': f'x.{uid}.f{len(exs)}', 'type': 'fill', 'q': e['zh'].replace(it['s'], '＿＿', 1), 'o': o, 'a': o.index(it['s']), 'en': e['en'], 'why': f'{it["s"]} {it["p"]}: {it["en"]}'})
            for e in sents[4:6]: exs.append({'id': f'x.{uid}.t{len(exs)}', 'type': 'translate', 'en': e['en'], 'a': [e['zh']], 'p': e['p']})
            gram = {'id': f'l.{uid}.0', 'title': '本课 · Theme and grammar', 'type': 'info', 'html': f'<p class="muted center">{title} · 第{N}单元</p><h2 class="display" style="text-align:center">{theme}</h2><p><b>Grammar focus:</b> <span class="hz">{focus}</span></p><p class="muted">Learn the pattern with the words in this unit; the example sentences use only characters you have met so far wherever possible.</p>'}
            lessons = [gram]
            nl = max(1, math.ceil(len(items) / 8))
            for li in range(nl):
                grp = items[li * len(items) // nl:(li + 1) * len(items) // nl]
                lessons.append({'id': f'l.{uid}.{li + 1}', 'title': '、'.join(x['s'] for x in grp[:4]) + ('…' if len(grp) > 4 else ''), 'type': 'new', 'items': [x['id'] for x in grp]})
            if exs: lessons.append({'id': f'l.{uid}.d', 'title': '练一练 · Drills', 'type': 'drill', 'ex': [x['id'] for x in exs]})
            texts = []
            if len(sents) >= 4:
                texts.append({'id': f't.{uid}', 'kind': 'reading', 'title': f'读一读 · {theme}', 'src': 'Example sentences from Tatoeba (CC BY 2.0 FR)', 'lines': sorted(sents, key=lambda e: len(e['zh']))[:10]})
                lessons.append({'id': f'l.{uid}.r', 'title': '读一读 · Read it all', 'type': 'text', 'text': texts[0]['id']})
            if review: lessons.append(review)
            u = {'id': uid, 'stage': stage, 'n': N, 'track': 'hsk', 'title': theme, 'en': f'{title} · Unit {N}', 'intro': f'<p><b>Grammar focus:</b> <span class="hz">{focus}</span></p>', 'items': items, 'chars': {}, 'texts': texts, 'exercises': exs, 'lessons': lessons,
                 'sents': [{'zh': e['zh'], 'p': e['p'], 'en': e['en']} for e in sents]}
        units.append(u)
        meta.append({'id': uid, 'n': N, 'title': u['title'], 'en': f'{len(u["items"])} words', 'ls': ','.join(l['id'].split('.')[-1] for l in u['lessons'])})
    os.makedirs(os.path.join(DATA, 'hsk'), exist_ok=True)
    json.dump({'stage': stage, 'level': lv, 'units': units}, open(os.path.join(DATA, 'hsk', f'hsk{lv}.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    nw = sum(len(u['items']) for u in units)
    stages.append({'n': stage, 'track': 'hsk', 'title': title, 'en': f'Units {first}–{unit_no} · {nw} words', 'pack': f'hsk/hsk{lv}.json', 'units': [], 'unitsMeta': meta})
    print(f'{title}: units {first}-{unit_no}, {nw} words, examples on {sum(1 for u in units for it in u["items"] if it.get("ex"))} words')

idx = {'version': 2, 'stages': [{'n': 1, 'track': 'p1', 'title': '部首 · Character structure', 'en': '17 radical units · about 200 characters', 'units': p1_units}] + stages}
json.dump(idx, open(os.path.join(DATA, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('words taught:', len(taken), '+ Part 1 characters', sum(1 for _ in p1_units) * 12)
