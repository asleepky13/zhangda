// Content linter. Run: node tools/validate.cjs   (exit 1 on errors)
const fs = require('fs'), path = require('path');
const dir = path.join(__dirname, '..', 'data');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const m = { exports: {} }; new Function('module', html.match(/<script id="core">([\s\S]*?)<\/script>/)[1])(m); const C = m.exports;
const syl = JSON.parse(fs.readFileSync(path.join(dir, 'syllables.json'), 'utf8'));
const SYL = new Set(Object.keys(syl).map(k => C.normBase(k.replace(/v/g, 'ü'))).concat(['er', 'm', 'n', 'ng', 'hm', 'o', 'me', 'ne', 'ei', 'dei', 'zhei', 'nang', 'den', 'cen', 'chua', 'zhuai', 'shei', 'miu', 'ma', 'ba', 'la', 'a', 'zi', 'de', 'le', 'ge', 'zhe', 'men', 'li', 'tou', 'mian', 'jie', 'qi', 'xi', 'ye', 'zhuo']));
for (const [k, v] of Object.entries(syl)) if ([...v].length !== 4) console.log('syllables.json: bad entry', k, v);
const idx = JSON.parse(fs.readFileSync(path.join(dir, 'index.json'), 'utf8'));
const errs = [], warns = [], ids = new Map(), words = new Map();
const E = (u, msg) => errs.push(`${u}: ${msg}`), Wn = (u, msg) => warns.push(`${u}: ${msg}`);
const units = [];
for (const st of idx.stages) {
  for (const f of st.units) { try { units.push(JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'))); } catch (e) { E(f, 'cannot parse: ' + e.message); } }
  if (st.pack) { try { const pk = JSON.parse(fs.readFileSync(path.join(dir, st.pack), 'utf8')); pk.units.forEach(u => units.push(u));
    const ids = pk.units.map(u => u.id).join(), meta = (st.unitsMeta || []).map(m => m.id).join(); if (ids !== meta) E(st.pack, 'unitsMeta out of sync with the pack'); } catch (e) { E(st.pack, 'cannot parse: ' + e.message); } }
}
const hskNote = { fewEx: 0, noChar: 0 };
const allChars = new Map();
units.forEach(u => Object.entries(u.chars || {}).forEach(([c, v]) => allChars.set(c, v)));
function checkPy(u, where, zh, p) {
  if (typeof zh !== 'string' || typeof p !== 'string') return E(u, `${where}: missing zh/p`);
  const a = C.align(zh, p);
  if (!a) { const nh = [...zh].filter(C.isHan).length, ns = p.trim().split(/\s+/).map(C.parseSyl).filter(Boolean).length; return E(u, `${where}: 「${zh}」 has ${nh} hanzi but ${ns} syllables: ${p}`); }
  for (const s of a) {
    const b = C.normBase(s.base.endsWith('r') && s.base !== 'er' ? s.base.slice(0, -1) : s.base);
    if (!SYL.has(b)) E(u, `${where}: unknown syllable "${s.base}" in ${p}`);
    if (s.hz === '一' && s.base === 'yi' && s.tone !== 1) Wn(u, `${where}: write 一 as citation yī (engine applies sandhi): ${zh}`);
    if (s.hz === '不' && s.base === 'bu' && s.tone === 2) Wn(u, `${where}: write 不 as citation bù: ${zh}`);
  }
  return a;
}
const reg = (u, id, kind) => { if (!id) return E(u, kind + ' without id'); if (ids.has(id)) E(u, `duplicate id ${id} (also in ${ids.get(id)})`); ids.set(id, u); };
let nItems = 0, nEx = 0, nLines = 0;
for (const u of units) {
  const U = u.id;
  ['id', 'stage', 'n', 'title', 'en', 'items', 'lessons'].forEach(k => u[k] == null && E(U, 'missing ' + k));
  const local = new Set();
  for (const it of u.items || []) {
    reg(U, it.id, 'item'); local.add(it.id); nItems++;
    ['k', 's', 'p', 'en'].forEach(k => !it[k] && E(U, `${it.id} missing ${k}`));
    checkPy(U, it.id, it.s, it.p);
    if (!['syl', 'rad'].includes(it.k)) {
      const wk = (u.track || 'core') + ':' + it.s; // a word may appear once per track
      if (words.has(wk)) E(U, `word 「${it.s}」 defined twice (${words.get(wk)})`); words.set(wk, it.id);
      if (!(it.ex && it.ex.length >= 2) && it.k !== 'char') { if (u.track === 'hsk') hskNote.fewEx++; else Wn(U, `${it.id}: fewer than 2 examples`); }
      for (const c of [...it.s].filter(C.isHan)) if (!allChars.has(c)) { if (u.track === 'hsk') hskNote.noChar++; else Wn(U, `char 「${c}」 (in ${it.id}) has no chars entry`); }
    }
    if (it.pair && !(u.items || []).some(x => x.id === it.pair)) E(U, `${it.id}: pair ${it.pair} not in unit`);
    (it.ex || []).forEach((e, i) => { checkPy(U, `${it.id} ex${i}`, e.zh, e.p); if (!e.en) E(U, `${it.id} ex${i} no en`); nLines++; if (!e.zh.includes(it.s.replace('儿', '')) && it.k !== 'syl') Wn(U, `${it.id} ex${i} doesn't contain the word: ${e.zh}`); });
  }
  for (const [c, v] of Object.entries(u.chars || {})) {
    if (!v.p || !v.m) E(U, `chars ${c} missing p/m`);
    else { const ps = C.parseSyl(v.p.split(/[,，\s]/)[0]); if (!ps || !SYL.has(C.normBase(ps.base))) E(U, `chars ${c}: bad pinyin ${v.p}`); }
  }
  for (const t of u.texts || []) {
    reg(U, t.id, 'text');
    t.lines.forEach((l, i) => { checkPy(U, `${t.id} line${i}`, l.zh, l.p); if (!l.en) E(U, `${t.id} line${i} no en`); nLines++; });
    (t.qs || []).forEach((q, i) => { if (q.o && (q.a == null || !q.o[q.a])) E(U, `${t.id} q${i} bad answer index`); if (!q.o && !q.ans) E(U, `${t.id} q${i} needs o/a or ans`); });
  }
  const exL = new Set();
  for (const x of u.exercises || []) {
    reg(U, x.id, 'exercise'); exL.add(x.id); nEx++;
    const T = x.type;
    if (['fill', 'syn', 'fix'].includes(T)) { if (!Array.isArray(x.o) || x.o[x.a] == null || !x.q) E(U, `${x.id}: needs q, o, a`); if (new Set(x.o).size !== x.o.length) E(U, `${x.id}: duplicate options`); }
    else if (T === 'order') { checkPy(U, x.id, x.zh, x.p); if (!x.en) E(U, `${x.id} needs en`); }
    else if (T === 'translate') { if (!x.en || !Array.isArray(x.a) || !x.a.length) E(U, `${x.id} needs en + a[]`); if (x.p) checkPy(U, x.id, x.a[0], x.p); }
    else if (T === 'tonepair') { if (!x.pairs || !x.pairs.every(p => p.length === 4)) E(U, `${x.id} pairs must be [hz,py,hz,py]`); else x.pairs.forEach(p => { checkPy(U, x.id, p[0], p[1]); checkPy(U, x.id, p[2], p[3]); }); }
    else if (T === 'zuci') { if (!x.c || !x.ok || !x.no) E(U, `${x.id} needs c, ok, no`); }
    else if (T === 'zaoju') { if (!x.w || !x.models || !x.models.every(s => s.includes(x.w))) E(U, `${x.id}: models must contain ${x.w}`); }
    else if (T === 'match') { if (!x.pairs || x.pairs.some(p => p.length !== 2)) E(U, `${x.id} pairs must be [a,b]`); }
    else if (T === 'essay') { if (!x.prompt) E(U, `${x.id} needs prompt`); }
    else E(U, `${x.id}: unknown type ${T}`);
  }
  const sc = u.scenario;
  if (sc) {
    reg(U, sc.id, 'scenario');
    if (!sc.nodes[sc.start]) E(U, 'scenario start missing');
    for (const [k, n] of Object.entries(sc.nodes)) {
      checkPy(U, `${sc.id}.${k}`, n.npc, n.p); if (!n.en) E(U, `${sc.id}.${k} no en`);
      if (!n.end) { if (!n.opts || !n.opts.length) E(U, `${sc.id}.${k} needs opts or end`);
        (n.opts || []).forEach((o, i) => { checkPy(U, `${sc.id}.${k}.opt${i}`, o.zh, o.p); if (!sc.nodes[o.next]) E(U, `${sc.id}.${k}.opt${i} next "${o.next}" missing`); if (!o.en) E(U, `${sc.id}.${k}.opt${i} no en`); }); }
    }
  }
  for (const l of u.lessons || []) {
    reg(U, l.id, 'lesson');
    (l.items || []).forEach(id => !local.has(id) && E(U, `${l.id}: item ${id} not in unit`));
    (l.ex || []).forEach(id => !exL.has(id) && E(U, `${l.id}: exercise ${id} not in unit`));
    if (l.type === 'text' && !(u.texts || []).some(t => t.id === l.text)) E(U, `${l.id}: text ${l.text} missing`);
    if (l.type === 'scenario' && !sc) E(U, `${l.id}: no scenario`);
    if (l.type === 'new' && ((l.items || []).length < 4 || l.items.length > 20)) Wn(U, `${l.id}: ${l.items.length} items (aim 4–20)`);
  }
  const used = new Set((u.lessons || []).flatMap(l => l.items || []));
  (u.items || []).forEach(it => !used.has(it.id) && E(U, `${it.id} not in any lesson`));
}
warns.forEach(w => console.log('warn ', w));
if (hskNote.fewEx) console.log(`note  HSK: ${hskNote.fewEx} words have fewer than 2 example sentences (open sentence data runs thin at higher levels)`);
errs.forEach(e => console.log('ERROR', e));
console.log(`${units.length} units · ${nItems} items · ${nEx} exercises · ${nLines} sentences/lines · ${allChars.size} chars · ${errs.length} errors · ${warns.length} warnings`);
process.exit(errs.length ? 1 : 0);
