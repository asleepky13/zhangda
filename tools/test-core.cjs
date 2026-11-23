// Unit tests for the pure logic in index.html <script id="core">. Run: node tools/test-core.cjs
const fs = require('fs'), path = require('path'), assert = require('assert');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const src = html.match(/<script id="core">([\s\S]*?)<\/script>/)[1];
const m = { exports: {} }; new Function('module', src)(m); const C = m.exports;
let n = 0; const t = (name, fn) => { fn(); n++; };
const spoken = (zh, p) => C.sandhi(C.align(zh, p)).map(s => C.markSyl(s.base, s.sp)).join(' ');

t('parse/mark', () => {
  assert.deepStrictEqual(C.parseSyl('mā'), { base: 'ma', tone: 1 });
  assert.deepStrictEqual(C.parseSyl('lv4'), { base: 'lü', tone: 4 });
  assert.deepStrictEqual(C.parseSyl('ma'), { base: 'ma', tone: 5 });
  assert.strictEqual(C.markSyl('hao', 3), 'hǎo'); assert.strictEqual(C.markSyl('gou', 3), 'gǒu');
  assert.strictEqual(C.markSyl('liu', 2), 'liú'); assert.strictEqual(C.markSyl('gui', 4), 'guì');
  assert.strictEqual(C.markSyl('lü', 4), 'lǜ'); assert.strictEqual(C.markSyl('dianr', 3), 'diǎnr');
});
t('split typed', () => {
  const S = new Set(['ni', 'hao', 'xian', 'xi', 'an', 'ma', 'zhong', 'guo']);
  const b = a => a.map(x => x.base + x.tone).join(' ');
  assert.strictEqual(b(C.splitTyped('ni3 hao3', S)), 'ni3 hao3');
  assert.strictEqual(b(C.splitTyped('ni3hao3', S)), 'ni3 hao3');
  assert.strictEqual(b(C.splitTyped('nǐhǎo', S)), 'ni3 hao3');
  assert.strictEqual(b(C.splitTyped('zhongguo2', S)), 'zhong5 guo2');
  assert.strictEqual(b(C.splitTyped("xi1'an1", S)), 'xi1 an1');
});
t('align + erhua', () => {
  const a = C.align('一点儿水。', 'yī diǎnr shuǐ');
  assert.strictEqual(a.length, 3); assert.strictEqual(a[1].hz, '点儿'); assert.ok(a[2].brk);
  assert.strictEqual(C.align('女儿', 'nǚ ér').length, 2);
  assert.strictEqual(C.align('你好', 'nǐ'), null);
});
t('sandhi', () => {
  assert.strictEqual(spoken('你好', 'nǐ hǎo'), 'ní hǎo');
  assert.strictEqual(spoken('不是', 'bù shì'), 'bú shì');
  assert.strictEqual(spoken('不好', 'bù hǎo'), 'bù hǎo');
  assert.strictEqual(spoken('是不是', 'shì bù shì'), 'shì bu shì');
  assert.strictEqual(spoken('一个', 'yī gè'), 'yí gè');
  assert.strictEqual(spoken('一天', 'yī tiān'), 'yì tiān');
  assert.strictEqual(spoken('一起', 'yī qǐ'), 'yì qǐ');
  assert.strictEqual(spoken('第一', 'dì yī'), 'dì yī');
  assert.strictEqual(spoken('十一', 'shí yī'), 'shí yī');
  assert.strictEqual(spoken('一月', 'yī yuè'), 'yī yuè');
  assert.strictEqual(spoken('一百', 'yī bǎi'), 'yì bǎi');
  assert.strictEqual(spoken('看一看', 'kàn yī kàn'), 'kàn yi kàn');
  assert.strictEqual(spoken('一二三', 'yī èr sān'), 'yī èr sān');
  assert.strictEqual(spoken('我很好', 'wǒ hěn hǎo'), 'wó hén hǎo');
  assert.strictEqual(spoken('姐姐', 'jiě jie'), 'jiě jie');
  assert.strictEqual(spoken('你好，我很好。', 'nǐ hǎo wǒ hěn hǎo'), 'ní hǎo wó hén hǎo');
  assert.strictEqual(spoken('好，你', 'hǎo nǐ'), 'hǎo nǐ'); // comma breaks the 3+3 run
  const s = C.sandhi(C.align('好吃', 'hǎo chī')); assert.ok(s[0].half);
  // word-grouped runs
  const dict = new Set(['你好', '老虎', '小狗', '小猫', '没有', '耳朵', '喜欢', '很好', '好吃']);
  const sp = (zh, p) => C.sandhi(C.align(zh, p), dict).map(x => C.markSyl(x.base, x.sp)).join(' ');
  assert.strictEqual(sp('你好你好', 'nǐ hǎo nǐ hǎo'), 'ní hǎo ní hǎo');
  assert.strictEqual(sp('小狗小猫', 'xiǎo gǒu xiǎo māo'), 'xiáo gǒu xiǎo māo');
  assert.strictEqual(sp('小老虎', 'xiǎo lǎo hǔ'), 'xiáo láo hǔ');
  assert.strictEqual(sp('老虎很好', 'lǎo hǔ hěn hǎo'), 'láo hǔ hén hǎo');
  assert.strictEqual(sp('没有耳朵', 'méi yǒu ěr duo'), 'méi yóu ěr duo');
  assert.strictEqual(sp('我也很喜欢', 'wǒ yě hěn xǐ huan'), 'wó yé hén xǐ huan');
  assert.strictEqual(sp('一个一个', 'yī gè yī gè'), 'yí gè yí gè');
  assert.strictEqual(sp('疼不疼', 'téng bù téng'), 'téng bu téng');
});
t('compare pinyin', () => {
  const tgt = C.sandhi(C.align('你好', 'nǐ hǎo')).map(s => ({ ...s, alt: [s.tone] }));
  assert.ok(C.comparePy(tgt, C.splitTyped('ni3 hao3')).ok);           // citation accepted
  assert.ok(C.comparePy(tgt, C.splitTyped('ni2 hao3')).ok);           // spoken accepted
  const r = C.comparePy(tgt, C.splitTyped('ni4 hao3'));
  assert.ok(!r.ok); assert.strictEqual(r.res[0].st, 'tone');
  const r2 = C.comparePy(tgt, C.splitTyped('hao3'));
  assert.strictEqual(r2.res[0].st, 'miss');
  const ju = [{ base: 'ju', tone: 2, sp: 2 }];
  assert.ok(C.comparePy(ju, C.splitTyped('jv2')).ok);
});
t('score heard pinyin', () => {
  const tgt = C.sandhi(C.align('你好', 'nǐ hǎo'));
  const H = s => s.split(' ').map(C.parseSyl);
  assert.strictEqual(C.scoreHeard(tgt, H('ni3 hao3')).base, 1);               // recogniser gives citation tones
  assert.strictEqual(C.scoreHeard(tgt, H('ni3 hao3')).tone, 1);
  const m = C.scoreHeard(C.align('买', 'mǎi'), H('mai4'));                      // said 卖 instead of 买
  assert.strictEqual(m.base, 1); assert.strictEqual(m.tone, 0); assert.strictEqual(m.res[0].st, 'tone');
  assert.ok(C.scoreHeard(tgt, H('ni3')).base < 0.85);                          // half the word missing
});
t('numbers & similarity', () => {
  assert.strictEqual(C.numToZh(10), '十'); assert.strictEqual(C.numToZh(15), '十五'); assert.strictEqual(C.numToZh(105), '一百零五');
  assert.strictEqual(C.numToZh(2024), '二千零二十四'); assert.strictEqual(C.numToZh(30000), '三万');
  assert.strictEqual(C.charSim('我有3个苹果', '我有三个苹果。'), 1);
  assert.ok(C.charSim('我有个苹果', '我有三个苹果') > 0.8);
  assert.deepStrictEqual(C.charDiff('我门', '我们').map(d => d.st), ['ok', 'miss']);
});
t('segment', () => {
  const d = new Map([['妈妈', 1], ['我', 1], ['爱', 1], ['爱心', 1]]);
  assert.deepStrictEqual(C.segment('我爱妈妈。', d).map(x => x.w), ['我', '爱', '妈妈', '。']);
});
t('fsrs', () => {
  const now = Date.UTC(2026, 0, 1);
  let c = C.newCard('x', 'reading');
  c = C.review(c, 3, now); assert.strictEqual(c.st, 1); assert.strictEqual(c.due - now, 10 * 6e4);
  c = C.review(c, 3, now + 6e5); assert.strictEqual(c.st, 2); assert.strictEqual(c.ivl, 4); // S0(Good)=3.71 → 4 days
  const s1 = c.s;
  c = C.review(c, 3, c.due); assert.ok(c.s > s1 * 2, 'stability grows on success: ' + c.s);
  const before = c.s;
  c = C.review(c, 1, c.due); assert.strictEqual(c.st, 3); assert.ok(c.s < before); assert.strictEqual(c.lapses, 1);
  let e = C.review(C.newCard('y', 'reading'), 4, now); assert.strictEqual(e.st, 2); assert.ok(e.ivl >= 13);
  let a = C.review(C.newCard('z', 'reading'), 1, now); assert.strictEqual(a.due - now, 6e4);
  for (let i = 0; i < 6; i++) { c = C.review({ ...c, st: 2 }, 1, now + i * 864e5 * 3); } assert.ok(c.leech);
  assert.ok(Math.abs(C.retr(10, 10) - 0.9) < 1e-9); // R(t=S) = 0.9 by construction
});
t('pitch: yin + tones', () => {
  const sr = 48000, buf = new Float32Array(2048);
  for (const f of [110, 200, 320]) { for (let i = 0; i < buf.length; i++) buf[i] = Math.sin(2 * Math.PI * f * i / sr) * 0.5 + 0.2 * Math.sin(4 * Math.PI * f * i / sr); const g = C.yin(buf, sr); assert.ok(Math.abs(g - f) / f < 0.02, `yin ${f} → ${g}`); }
  // synthetic syllables: semitone shapes over a 200 Hz base
  const mk = (shape, t0, dur) => { const out = []; for (let k = 0; k <= 20; k++) { const x = k / 20; out.push({ t: t0 + x * dur, f: 200 * Math.pow(2, shape(x) / 12), e: 0.1 }); } return out; };
  const T = { 1: x => 4, 2: x => -1 + 6 * x, 3: x => x < 0.6 ? -2 - 4 * x : -4.4 + 9 * (x - 0.6), 4: x => 5 - 10 * x };
  for (const tone of [1, 2, 3, 4]) {
    const track = [...mk(T[tone], 0, 0.35), ...mk(T[1], 0.6, 0.3)]; // target syllable then a reference level tone
    const segs = C.pitchSegments(track, 2);
    assert.strictEqual(segs.length, 2);
    assert.strictEqual(C.classifyTone(segs[0]).tone, tone, 'tone ' + tone + ' ' + JSON.stringify(C.classifyTone(segs[0])));
  }
  // one long voiced run must still split into 2 syllables
  const glued = [...mk(T[4], 0, 0.3), ...mk(T[2], 0.31, 0.3)].map((p, i) => ({ ...p, e: i === 21 ? 0.01 : 0.1 }));
  assert.strictEqual(C.pitchSegments(glued, 2).length, 2);
});
console.log(`core: ${n} test groups passed`);
{ const r = C.scoreHeard(C.align('谢谢', 'xiè xie'), ['xie4', 'xie4'].map(C.parseSyl)); assert.strictEqual(r.tone, 1, 'neutral tone tolerated'); console.log('neutral-tone grading ok'); }
// realistic tone variants with jitter: accuracy per variant, with and without a speaker baseline
{
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647 - 0.5);
  const B = 200, st = f => 12 * Math.log2(f);
  const syl = (shape, t0, dur, gapAt) => { const out = []; for (let k = 0; k <= 24; k++) { const x = k / 24; if (gapAt && x > gapAt && x < gapAt + 0.22) continue; out.push({ t: t0 + x * dur, f: B * Math.pow(2, (shape(x) + rnd() * 0.8) / 12), e: 0.1 }); } return out; };
  const V = {
    'T3 classic 214': [3, x => x < 0.55 ? -2 - 7 * x : -5.9 + 11 * (x - 0.55)],
    'T3 late dip 213': [3, x => x < 0.72 ? -2.5 - 4.5 * x : -5.7 + 13 * (x - 0.72)],
    'T3 shallow 212': [3, x => x < 0.5 ? -3 - 6 * x : -6 + 5 * (x - 0.5)],
    'T3 creaky': [3, x => x < 0.5 ? -3 - 7 * x : -6.5 + 6 * (x - 0.5), 0.42],
    'T2 with dip': [2, x => x < 0.25 ? -1 - 3 * x : -1.75 + 8.5 * (x - 0.25)],
    'T2 plain': [2, x => -1.5 + 7 * x],
    'T4': [4, x => 5 - 11 * x],
    'T1 level': [1, x => 4.2 - 0.6 * x],
  };
  const report = [];
  for (const [name, [want, f, gap]] of Object.entries(V)) for (const withBase of [false, true]) {
    let hit = 0; const N = 25;
    for (let r = 0; r < N; r++) {
      // syllable followed by a mid level reference syllable, like a real two-syllable word
      const track = [...syl(f, 0, 0.36, gap), ...syl(() => 0.5, 0.55, 0.3)];
      const seg = C.pitchSegments(track, 2)[0];
      if (C.classifyTone(seg, withBase ? { base: st(B) } : {}).tone === want) hit++;
    }
    report.push(`${name}${withBase ? ' +base' : ''}: ${hit}/${N}`);
    assert.ok(hit / N >= 0.88, `${name}${withBase ? ' with base' : ''}: only ${hit}/${N}`);
  }
  // half-third: low falling 3rd tone before another tone; only distinguishable from T4/T1 with a baseline
  let hh = 0; for (let r = 0; r < 25; r++) { const track = [...syl(x => -3 - 3 * x, 0, 0.3), ...syl(x => 4, 0.5, 0.3)]; if (C.classifyTone(C.pitchSegments(track, 2)[0], { base: st(B) }).tone === 3) hh++; }
  report.push(`T3 half-third +base: ${hh}/25`); assert.ok(hh >= 22, 'half-third ' + hh);
  // Taiwan accent: T2 dips low and late, T3 is a low fall; standard shapes must still work in tw mode
  const TW = { 'TW T2 dip-rise': [2, x => x < 0.5 ? -1 - 4 * x : -3 + 6 * (x - 0.5)], 'TW T2 deep': [2, x => x < 0.45 ? -1.5 - 5 * x : -3.75 + 7 * (x - 0.45)], 'TW T3 low fall': [3, x => -2.5 - 4 * x],
    'TW T2 plain': [2, x => -1.5 + 7 * x], 'TW T3 full 214': [3, x => x < 0.55 ? -2 - 7 * x : -5.9 + 11 * (x - 0.55)], 'TW T4': [4, x => 5 - 11 * x], 'TW T1': [1, x => 4.2 - 0.6 * x] };
  for (const [name, [want, f]] of Object.entries(TW)) {
    let hit = 0; for (let r = 0; r < 25; r++) { const track = [...syl(f, 0, 0.36), ...syl(() => 0.5, 0.55, 0.3)]; const r0 = C.classifyTone(C.pitchSegments(track, 2)[0], { base: st(B), tw: true }); if (r0.tone === want || (want === 3 && r0.dip)) hit++; }
    report.push(`${name} +base: ${hit}/25`); assert.ok(hit >= 22, `${name}: only ${hit}/25`);
  }
  console.log('tone variants:\n  ' + report.join('\n  '));
}
