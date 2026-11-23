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
