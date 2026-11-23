# 长大 Zhǎngdà: architecture

A mobile PWA that walks you through Mandarin the way a native child learns it, from 儿歌 to 高考 essays and the news.

## Files

```
index.html            engine: UI, SRS, exercises, speech in/out, pitch, handwriting, library, scenarios, dashboard
sw.js                 offline cache (app shell + data + Hanzi Writer stroke data as you use it)
manifest.webmanifest  install to home screen
icon.svg
data/index.json       course manifest: stages → unit file list (add a unit = drop a file + add one line)
data/syllables.json   pinyin chart: every syllable × 4 tones → a character the TTS can say
data/s1u01.json …     one file per unit
tools/validate.cjs    content linter: pinyin↔hanzi alignment, tone marks, ids, char coverage
tools/test-core.cjs   unit tests for FSRS, pinyin parsing, tone sandhi, segmentation, grading
serve.cjs             zero-dependency static server for local testing
```

## Data schema (one unit file)

```jsonc
{
  "id": "s1u04", "stage": 1, "n": 4,
  "title": "家人", "en": "Family", "intro": "…",
  "items": [{
    "id": "w.爸爸",          // unique across the course; prefix w. word, y. syllable, c. character, r. radical, cy. 成语
    "k": "word",            // word | syl | char | rad | chengyu | xhy (歇后语) | suyu | slang | mw
    "s": "爸爸", "t": "爸爸",// simplified / traditional (t only when different)
    "p": "bà ba",           // citation tones, one syllable per hanzi, neutral tone unmarked; engine applies sandhi
    "pos": "n", "en": "dad", "zh": "父亲",   // zh = Chinese definition, shown once glosses switch to Chinese
    "mw": "个", "reg": "spoken", "hsk": 1,
    "col": ["我爸爸", "爸爸妈妈"],
    "ex": [{ "zh": "我爸爸很高。", "p": "wǒ bà ba hěn gāo", "en": "My dad is tall." }],
    "note": "optional usage / origin note"
  }],
  "chars": { "爸": { "p": "bà", "m": "dad", "r": "父", "c": ["父", "巴"], "h": "memory hook", "t": "trad" } },
  "texts": [{ "id": "t.s1u04.1", "kind": "rhyme|story|poem|classical|essay", "title": "…", "src": "traditional|original|<author, era>",
              "lines": [{ "zh": "…", "p": "…", "en": "…", "mod": "modern rendering (classical only)" }],
              "notes": ["…"], "qs": [{ "q": "…", "o": ["…"], "a": 0 }, { "q": "…", "ans": "model answer" }] }],
  "exercises": [{ "id": "x.s1u04.1", "type": "fill|fix|order|translate|tonepair|zuci|zaoju|syn|cloze|poemline|match", "...": "type-specific" }],
  "scenario": { "id": "sc.s1u04", "title": "…", "setting": "…", "start": "a",
                "nodes": { "a": { "npc": "…", "p": "…", "en": "…", "opts": [{ "zh": "…", "p": "…", "en": "…", "next": "b", "score": 2, "fb": "why" }] },
                           "z": { "npc": "…", "p": "…", "en": "…", "end": true } } },
  "lessons": [{ "id": "l.s1u04.1", "title": "…", "type": "new|text|drill|scenario", "items": ["w.爸爸"], "text": "t.…", "ex": ["x.…"] }]
}
```

Word families, the character dictionary, look-alike detection, sentence-building tiles, cloze blanks and most exercises are derived by the engine from the items, so content files hold only facts, not generated drills. Authored `exercises` cover what can't be derived: near-synonyms, error correction, particle and complement blanks, 组词 and 造句 prompts.

## SRS model

- One card per **item × skill**: `reading`, `writing`, `listening`, `speaking` (syllable items: listening + speaking; authored exercises: one `drill` card). Each card has its own FSRS state, so one word can be mature in reading and brand new in writing.
- **FSRS-4.5** with default weights, target retention 0.90 (adjustable). Learning steps 1 min → 10 min, relearning 10 min, then FSRS intervals. Same-day steps don't change stability.
- Grades: Again/Hard/Good/Easy. Auto-grading maps exercise results: wrong → Again; right with errors or slow → Hard; right → Good; you can override with the buttons after any answer.
- Queue: due reviews, all skills interleaved, come first. New lessons unlock only once the due queue is empty, capped by the daily new limit. Wrong answers come back 3–6 cards later in the same session and go to the weak deck with the reason (tone, look-alike, missing syllable, collocation, register).
- Leeches: 6 lapses on a card flags it. Leech reviews show the component breakdown, memory hook and word family before you answer.
- Scaffolding fades per card: pinyin over characters while reading stability < 3 days, pinyin on tap < 21 days, none after (global override in settings). Listening speed goes 0.6x → 0.9x → 1.15x as listening stability grows. Glosses switch from English to Chinese definitions from Stage 3 on.
- Gates: unit checkpoint (24 production questions across all four skills plus drills) needs 85% to unlock the next unit. A stage exam (40 questions, cumulative) unlocks the next stage.

## Exercise map

| Skill | First exposure | Later (production) |
|---|---|---|
| reading | characters → meaning (multiple choice) | type the pinyin with tones, then recall the meaning; meaning in a sentence; sentence building |
| writing | stroke-order tracing with outline; component assembly | handwrite from memory, stroke-by-stroke correction; meaning → character among look-alikes |
| listening | hear → pick meaning | hear → type pinyin with tones at growing speed; sentence dictation (type characters) |
| speaking | shadow the audio (recognition + pitch contour) | meaning → say it (recognition + pitch); translate EN→ZH by voice |
| syllable | tone ID / minimal pair | say the syllable, pitch graded per tone |
| drill | fill-in, error correction, synonyms, 组词, 造句, order, translate, cloze, poem line, 成语 match |

Plus: recitation (listen → read along → prompted → from memory → handwrite), branching scenarios, reading-speed drills, essays with rule-based feedback, checkpoints and stage exams.

## Screen map

```
Today ── review queue → new lesson → weak words / cram
Course ── stages → units → lessons · checkpoint · stage exam
Library ── texts unlocked so far → reader (tap lookup, pinyin, translation, audio) → recitation · questions
Dictionary ── everything learned → entry (strokes, components, family, examples, mastery per skill)
More ── dashboard · pinyin chart · scenarios · settings (limits, voice, scaffolding, export/import)
```

## Course outline

Word targets are new words per unit; 成语 and other decks are on top.

### Stage 1 幼儿 (10 units, 335 items, 152 drills, 536 sentences/lines): built, see `data/s1u01–10.json`

| # | Unit | Focus | Items |
|---|---|---|---|
| 1 | 四个声调 | four tones, neutral tone, 3+3 / 不 / 一 sandhi, half-third tone, 儿化 | 60 |
| 2 | 声母和韵母 | all initials and finals, zh/z ch/c sh/s, j q x, ü, -n/-ng minimal pairs | 42 |
| 3 | 笔画和部首 | 8 stroke types, stroke-order rules, 12 core radicals, first pictographs | 36 |
| 4 | 我的家 | family, 是, 叫, 有, 的, pronouns | 37 |
| 5 | 我的身体 | body, basic verbs, 疼 | 27 |
| 6 | 数字和颜色 | 一–百, 两, 几, 个, 岁, colors | 28 |
| 7 | 小动物 | animals, measure words 只/条/头/匹 | 27 |
| 8 | 好吃的 | food and drink, 要/想, 饿/渴/饱 | 28 |
| 9 | 我的家和玩具 | home, toys, 在 + place, 里/上/下 | 26 |
| 10 | 我的心情 | feelings, politeness, 因为 (first look) | 24 |

### Stage 2 小学低年级 (24 units, ~1,400 words, ~900 new characters)

| # | Unit | Focus | Words |
|---|---|---|---|
| 1 | 识字：天地日月 | 象形字, nature pictographs | 50 |
| 2 | 上学了 | school, 是/有/在 sentences | 60 |
| 3 | 几点了 | time, days, 年月日 | 60 |
| 4 | 天气和四季 | weather, seasons | 60 |
| 5 | 我想问问 | 吗/呢/什么/谁/哪儿/怎么 | 55 |
| 6 | 去商店 | money, 个本张支件 | 65 |
| 7 | 古诗：咏鹅 · 春晓 | first Tang poems, recitation | 60 |
| 8 | 我做完了 | action verbs, 了 | 60 |
| 9 | 我的一天 | routine, 着/过 | 60 |
| 10 | 坐车去 | transport, directions, 的/地/得 | 65 |
| 11 | 公园里 | 比, 没有…那么 | 60 |
| 12 | 古诗：静夜思 · 悯农 | | 60 |
| 13 | 寓言：守株待兔 | fable reading | 50 |
| 14 | 我生病了 | doctor visit scenario | 60 |
| 15 | 三字经（选） | rhythm of classical lines | 45 |
| 16 | 过春节 | Spring Festival, red envelopes, relatives' questions | 65 |
| 17 | 花草树木 | plants, nature | 60 |
| 18 | 寓言：拔苗助长 · 画蛇添足 | | 50 |
| 19 | 我会游泳 | sports, 能/会/可以 | 60 |
| 20 | 弟子规与礼貌 | manners, 请/让 | 50 |
| 21 | 城市和乡下 | places | 60 |
| 22 | 把字句 | 把 | 55 |
| 23 | 被字句 | 被 | 55 |
| 24 | 古诗：登鹳雀楼 · 江雪 + 小狐狸 stories | stage review | 55 |

### Stage 3 小学高年级 (28 units, ~2,000 words, 成语 +150)

1 成语：亡羊补牢 · 刻舟求剑 · 2 结果补语 · 3 趋向补语 · 4 可能补语 · 5 女娲补天 · 6 后羿射日 · 嫦娥奔月 · 7 牛郎织女 · 8 虽然…但是 / 因为…所以 · 9 不但…而且 / 一边…一边 · 10 记叙文：写一件事 · 11 李白：望庐山瀑布 · 赠汪伦 · 12 词入门：忆江南 · 13 西游记：石猴出世 · 14 西游记：大闹天宫 · 15 三国：桃园结义 · 16 三国：草船借箭 · 17 水浒：武松打虎 · 18 红楼梦：黛玉进府 · 19 即使…也 / 只要…就 / 只有…才 · 20 写日记 · 21 写信 · 22 写人：外貌与性格 · 23 写景 · 24 成语：井底之蛙 · 狐假虎威 · 25 校园生活（操场吵架） · 26 生日会 · 27 古诗：游子吟 · 清明 · 枫桥夜泊 · 28 作文：我的理想. About 70 words each.

### Stage 4 初中 (30 units, ~2,600 words, 成语 +150)

1 文言：之 · 2 而 · 以 · 3 其 · 于 · 4 者 · 也 · 乎 · 矣 · 5 论语（学而） · 6 论语（为政 · 里仁） · 7 孟子：鱼我所欲也 · 8 庄子：庖丁解牛 · 濠梁之辩 · 9 世说新语：咏雪 · 陈太丘与友期 · 10 陶渊明：饮酒 · 归园田居 · 11 李白：月下独酌 · 将进酒 · 12 杜甫：春望 · 绝句 · 13 王维：山居秋暝 · 鹿柴 · 14 白居易：卖炭翁 · 钱塘湖春行 · 15 苏轼：水调歌头 · 16 李清照：如梦令 · 声声慢 · 17 修辞：比喻 · 拟人 · 18 排比 · 夸张 · 对偶 · 19 说明文 · 20 议论文 · 21 鲁迅：故乡（节选） · 22 鲁迅：孔乙己（节选） · 23 朱自清：背影 · 24 朱自清：春 · 25 现代散文（original passages in the style of later authors） · 26 友谊与辩论 · 27 科技与生活 · 28 环境 · 29 孔子与屈原 · 30 中考作文. About 85 words each.

### Stage 5 高中 (30 units, ~2,800 words, 成语 +120)

1–2 史记：鸿门宴 · 3 廉颇蔺相如列传 · 4–5 出师表 · 6 桃花源记 · 7 岳阳楼记 · 8 醉翁亭记 · 9 前赤壁赋 · 10 劝学 · 11 师说 · 12 杜甫登高 · 琵琶行 · 13 念奴娇 · 赤壁怀古 · 14 雨霖铃 · 青玉案 · 15 书面语与口语 · 16 关联词进阶 · 17 高考材料作文 · 18 议论文结构 · 19–22 graded novella 《江边的夏天》 (original, serialized) · 23–25 朝代：先秦到近代 · 26 节日与习俗 · 27 儒释道 · 28 饮食与地方菜 · 29 南北差异 · 30 大学宿舍. About 95 words each.

### Stage 6 成人 (30 units, ~2,600 words, 成语 +80, slang 150, 歇后语 60, 俗语 120)

1 新闻体 · 2 经济新闻 · 3 社会新闻 · 4 国际新闻 · 5 求职面试 · 6 职场沟通 · 7 商务谈判 · 8 正式邮件与公文 · 9 合同用语 · 10 论文写作 · 11 讲座与报告 · 12 访谈（快速语流） · 13 播客式对话 · 14 争论与说服 · 15 笑话 · 16 相声与文字游戏 · 17 网络语言：yyds · 绝绝子 · 破防 · 18 内卷 · 躺平 · 摆烂 · 19 口语里的成语 · 20 歇后语与俗语 · 21 北方话与儿化 · 22 南方口音 · 23 台湾与大陆用语 · 24 手写体 · 25 书法：楷行草 · 26 婚宴敬酒 · 27 房东纠纷 · 28 安慰人 · 29 饭桌上讲故事 · 30 观点文章与说服文. About 85 words each.

Total ≈ 11,600 words plus decks, covering HSK 3.0 levels 1–9 and the 3,500 常用字.
