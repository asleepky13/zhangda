# Practice Bank (for the app)

This tab is the machine-readable source for the practice app: exercise rules plus per-unit data. Every unit's data is in fenced CSV blocks so it can be parsed directly.

## App spec: exercise types and test rules

The app should generate questions from each unit's data, not store fixed tests. Each unit gives 12 items, about 25 words, 20 sentences, 10 authored questions and a reading with 4 questions. Run through the 24 exercise types below, that comes to roughly 350–400 distinct questions per unit, over 10 times the 25 in the doc's unit tests. Shuffled options and random blanks make repeats rarer still.

**Exercise types**

| # | Type | Skill | Built from | How to generate | How to grade |
| --- | --- | --- | --- | --- | --- |
| 1 | Flashcard review | all | items, words | Spaced repetition (FSRS or SM-2), separate schedule per skill | Again / Hard / Good / Easy |
| 2 | Meaning → character | reading | items, words | Show English (+ pinyin toggle); 4 options: answer + 2 same-unit + 1 from `lookalikes` | Tap |
| 3 | Character → meaning | reading | items, words | Show character; 4 English options from the same unit | Tap |
| 4 | Pinyin → character | reading | items | Show pinyin; hard mode includes homophones (e.g. 游 / 油 yóu) | Tap |
| 5 | Listen → character | listening | items, words | Play TTS; 4 character options | Tap |
| 6 | Name the radical | structure | items | Show character; pick its radical from 4–6 radical tiles | Tap |
| 7 | Assemble the character | structure | items (`radical`, `component`) | Drag one radical tile + one component tile into two slots; 4 decoys each | Both slots right |
| 8 | Radical sort | structure | items from 2–4 units | Drag 8–9 characters into radical bins | Each drop checked |
| 9 | Word builder | vocabulary | `words` | Show English; drag 2–3 character tiles (with 3 decoys) into order | Exact match |
| 10 | Fill the blank | grammar, reading | sentences (`targets`) | Blank one target; options = answer + same-radical and `lookalikes` characters | Tap |
| 11 | Spot the mistake | structure | sentences + `lookalikes` | Swap one target for a look-alike; the learner taps the wrong character, then picks the right one | Both steps |
| 12 | Sentence builder | grammar | sentences (`tokens`) | Show English; drag shuffled tokens (punctuation excluded) into order | Exact token order |
| 13 | Translate (choose) | reading | sentences | English → pick the Chinese from 4 sentences in the unit | Tap |
| 14 | Translate (write) | writing | sentences | English → type or handwrite the Chinese | All target characters present, and at least 80% of characters matching |
| 15 | Dictation | listening, writing | sentences | Play TTS (slow, then normal); learner writes it | Same as 14 |
| 16 | Speak it | speaking | items, words, sentences | Show English; learner says it; speech-to-text | At least 80% character overlap; if speech-to-text is unavailable, self-grade |
| 17 | Shadowing | speaking | sentences, reading | Play a line, learner repeats; play back both | Self-grade |
| 18 | Write from memory | writing | items, words | Show English + pinyin; learner draws on a 田字格 canvas; reveal the answer overlaid | Self-grade; optional stroke check |
| 19 | Trace | writing | items | Faint character under the canvas | Self-grade |
| 20 | Match race | reading | items, words | 6 character–meaning pairs against a timer; keep a best time | Time |
| 21 | Speed round | reading | items, words | 60 seconds of types 2/3, auto-advance | Score |
| 22 | Error correction | grammar | `authored` type `error` | Show the wrong sentence; learner writes the fix | Matches `answer` |
| 23 | Dialogue completion | speaking, grammar | `authored` type `dialogue` | Show line A; pick or say reply B | Tap or speech match |
| 24 | Reading + questions | reading | `reading` | Passage with tap-to-hear; 4 multiple-choice questions | Tap |

**Test assembly (so no two tests are the same)**

- **Unit test: 25 questions**, drawn at random every time: 6 × type 18, 4 × type 10, 3 × type 11, 3 × type 12, 2 × type 14, 2 × type 15, 2 × type 7, 2 × type 22 or 23, 1 × type 16. Never reuse the same sentence twice in one test.
- **Review test (every 4 units): 40 questions** from those units, using the same mix. Half the slots go to the learner's weakest items, ranked by lapse count.
- **Final test: 60 questions** across all units, plus one full reading.
- **Pass mark: 85%.** Every miss resets that item's schedule for that skill, and it reappears later in the same session.
- **Never repeat:** keep the last 3 test seeds per unit and reject any new draw that shares more than 30% of its questions with them.

## Data format

Each unit section has the same four blocks in the same order, so a parser can split on the unit headings (`P1-U01`, `HSK1-U01`) and read the fenced blocks under each. A field containing a comma is wrapped in double quotes.

| Block | Columns | Notes |
| --- | --- | --- |
| `items` | zh, py, en, radical, component, words, lookalikes | `component` is the non-radical part (— = not assemblable). `words` = `word/pinyin/meaning` separated by ` ;  `. `lookalikes` = space-separated characters used as hard distractors |
| `sentences` | id, tokens, en, targets | `tokens` space-separated (punctuation is its own token; drop it in the sentence builder). `targets` = the unit's characters in the sentence, used for blanks and swaps |
| `authored` | id, type, prompt, answer, options, note | `type` is `error` or `dialogue`. `options` separated by `/` and include the answer |
| `reading` | a text block, then id, question, answer, options | An original passage built from the unit's words, with 4 multiple-choice questions |

The HSK units use the same format. Their `radical` column holds the main character's radical and `component` is — for multi-character words.

## P1-U01 氵 water

```csv
zh,py,en,radical,component,words,lookalikes
河,hé,river,氵,可,"河流/héliú/river; 黄河/Huánghé/Yellow River",何 可 阿
海,hǎi,sea,氵,每,"大海/dàhǎi/the sea; 海边/hǎibiān/seaside",每 梅 悔
洗,xǐ,wash,氵,先,"洗手/xǐshǒu/wash hands; 洗澡/xǐzǎo/shower",先 选
湖,hú,lake,氵,胡,"湖边/húbiān/lakeside; 西湖/Xīhú/West Lake",胡 糊
汤,tāng,soup,氵,—,"喝汤/hē tāng/have soup; 汤圆/tāngyuán/sweet rice balls",场 扬 杨
酒,jiǔ,alcohol,氵,酉,"啤酒/píjiǔ/beer; 酒店/jiǔdiàn/hotel",洒 酉
游,yóu,swim; travel,氵,—,"游泳/yóuyǒng/swim; 旅游/lǚyóu/travel",旅 族
清,qīng,clear,氵,青,"清楚/qīngchu/clear; 清水/qīngshuǐ/clean water",请 情 晴 青
没,méi,not have,氵,殳,"没有/méiyǒu/not have; 没关系/méi guānxi/it's OK",设 投
汗,hàn,sweat,氵,干,"出汗/chūhàn/sweat; 汗水/hànshuǐ/sweat",干 汁 汉
流,liú,flow,氵,—,"流利/liúlì/fluent; 流行/liúxíng/popular",硫 留
油,yóu,oil,氵,由,"加油/jiāyóu/refuel; come on!; 石油/shíyóu/petroleum",由 抽 邮
```

```csv
id,tokens,en,targets
P1U01-S01,我 每天 早上 都 要 洗澡 。,I shower every morning.,洗
P1U01-S02,他的 中文 说得 很 流利 。,He speaks Chinese fluently.,流
P1U01-S03,天气 太 热 了 ， 我 出了 很多 汗 。,"It's too hot, I sweated a lot.",汗
P1U01-S04,我们 周末 去 海边 游泳 吧 。,Let's go swimming at the beach this weekend.,海 游
P1U01-S05,这碗 汤 有点儿 咸 ， 可是 很 好喝 。,"This soup is a bit salty, but it tastes good.",汤
P1U01-S06,老师 讲得 很 清楚 ， 我 都 听懂了 。,"The teacher explained clearly, I understood everything.",清
P1U01-S07,没关系 ， 我们 明天 再 去 湖边 。,"It's OK, we'll go to the lake tomorrow.",没 湖
P1U01-S08,这首歌 现在 很 流行 。,This song is popular right now.,流
P1U01-S09,吃饭 以前 要 先 洗手 。,Wash your hands before eating.,洗
P1U01-S10,我 没有 钱 了 。,I'm out of money.,没
P1U01-S11,那条 河 很 长 。,That river is very long.,河
P1U01-S12,他 不 喝 酒 。,He doesn't drink alcohol.,酒
P1U01-S13,我的 车 没 油 了 。,My car is out of gas.,没 油
P1U01-S14,比赛 快 开始 了 ， 加油 ！,"The match is about to start, go for it!",油
P1U01-S15,我 想 去 海边 看看 大海 。,I want to go to the seaside to see the ocean.,海
P1U01-S16,夏天 我们 常常 去 湖里 游泳 。,In summer we often swim in the lake.,湖 游
P1U01-S17,你 听 清楚 了 吗 ？,Did you hear clearly?,清
P1U01-S18,黄河 是 中国 第二 长 的 河 。,The Yellow River is China's second-longest river.,河
P1U01-S19,喝 了 酒 不能 开车 。,Don't drive after drinking.,酒
P1U01-S20,他 跑完 步 ， 一身 都是 汗 。,"After his run, he was covered in sweat.",汗
```

```csv
id,type,prompt,answer,options,note
P1U01-A01,error,我想喝一杯啤洒。,我想喝一杯啤酒。,,洒 (sǎ) means sprinkle; 酒 has the extra stroke inside
P1U01-A02,error,老师讲得很请楚。,老师讲得很清楚。,,Clear is water (氵) not speech (讠)
P1U01-A03,error,我们去胡边走走吧。,我们去湖边走走吧。,,胡 is only the sound part; a lake needs 氵
P1U01-A04,error,我设有时间。,我没有时间。,,设 (shè) means set up
P1U01-A05,error,他出了很多干。,他出了很多汗。,,干 is only the sound part
P1U01-A06,error,我的车没由了。,我的车没油了。,,Oil needs 氵
P1U01-A07,dialogue,你喜欢游泳吗？,喜欢，我常常去海边游泳。,"喜欢，我常常去海边游泳。 / 我不喝酒。 / 汤很好喝。 / 没关系。",
P1U01-A08,dialogue,对不起，我来晚了。,没关系。,没关系。 / 加油！ / 我洗澡了。 / 那条河很长。,
P1U01-A09,dialogue,这个汤怎么样？,有点儿咸，可是很好喝。,"有点儿咸，可是很好喝。 / 我没有钱。 / 他不喝酒。 / 我去湖边。",
P1U01-A10,dialogue,明天比赛，我有点儿紧张。,别紧张，加油！,别紧张，加油！ / 我洗手了。 / 这是黄河。 / 我喜欢喝汤。,
```

```text
我家旁边有一个湖。夏天的时候，我常常和朋友去湖里游泳。游完泳，我们都很饿，就去湖边的小饭馆喝汤。那里的鱼汤很清，也很好喝。我朋友喜欢喝啤酒，可是我不喝酒，我喝茶。
```

```csv
id,question,answer,options
P1U01-R01,我家旁边有什么？,湖,湖 / 河 / 海 / 山
P1U01-R02,他们夏天常常做什么？,游泳,游泳 / 喝酒 / 洗澡 / 唱歌
P1U01-R03,那里的鱼汤怎么样？,很清，很好喝,很清，很好喝 / 太咸了 / 很贵 / 没有汤
P1U01-R04,“我”喝什么？,茶,茶 / 啤酒 / 汤 / 水
```

## P1-U02 艹 grass

```csv
zh,py,en,radical,component,words,lookalikes
草,cǎo,grass,艹,早,"草地/cǎodì/lawn; 草莓/cǎoméi/strawberry",早 革 菜
花,huā,flower; spend,艹,化,"花园/huāyuán/garden; 花钱/huāqián/spend money",化 华 货
茶,chá,tea,艹,—,"喝茶/hē chá/drink tea; 茶叶/cháyè/tea leaves",菜 余
菜,cài,vegetable; dish,艹,采,"点菜/diǎncài/order food; 蔬菜/shūcài/vegetables",采 彩 踩 茶
药,yào,medicine,艹,约,"吃药/chī yào/take medicine; 药店/yàodiàn/pharmacy",约 的 钓
苹,píng,apple (in 苹果),艹,平,"苹果/píngguǒ/apple",平 评 萍
英,yīng,English; hero,艹,央,"英语/Yīngyǔ/English; 英雄/yīngxióng/hero",央 映
节,jié,festival; section,艹,卩,"节日/jiérì/holiday; 春节/Chūnjié/Spring Festival; 节目/jiémù/show",卫 印
苦,kǔ,bitter,艹,古,"辛苦/xīnkǔ/hard-working; 痛苦/tòngkǔ/painful",古 若
落,luò,fall,艹,洛,"降落/jiàngluò/land (plane); 落后/luòhòu/fall behind",洛 络 路
蓝,lán,blue,艹,监,"蓝色/lánsè/blue; 蓝天/lántiān/blue sky",监 篮 盐
获,huò,obtain,艹,—,"获得/huòdé/win; 收获/shōuhuò/harvest",犹 狄
```

```csv
id,tokens,en,targets
P1U02-S01,春节 是 中国 最 重要 的 节日 。,Spring Festival is China's most important holiday.,节
P1U02-S02,你 工作 太 辛苦 了 ， 休息 一下 吧 。,"You work too hard, take a rest.",苦
P1U02-S03,感冒 了 就 去 药店 买 点儿 药 。,"If you catch a cold, go buy some medicine at the pharmacy.",药
P1U02-S04,服务员 ， 我们 要 点菜 。,"Waiter, we'd like to order.",菜
P1U02-S05,飞机 快要 降落 了 。,The plane is about to land.,落
P1U02-S06,她 每天 花 很多 时间 学 英语 。,She spends a lot of time studying English every day.,花 英
P1U02-S07,秋天 到 了 ， 树叶 都 落下来 了 。,"Autumn has come, the leaves have all fallen.",落
P1U02-S08,他 在 比赛 中 获得 了 第一名 。,He won first place in the competition.,获
P1U02-S09,你 喝 茶 还是 喝 咖啡 ？,Do you drink tea or coffee?,茶
P1U02-S10,天空 是 蓝色 的 。,The sky is blue.,蓝
P1U02-S11,这个 药 很 苦 。,This medicine is very bitter.,药 苦
P1U02-S12,我 买了 一斤 苹果 。,I bought a jin (half a kilo) of apples.,苹
P1U02-S13,你 最 喜欢 哪个 电视 节目 ？,Which TV show do you like best?,节
P1U02-S14,我 给 妈妈 买了 一些 花 。,I bought some flowers for my mom.,花
P1U02-S15,你 喜欢 吃 中国菜 吗 ？,Do you like Chinese food?,菜
P1U02-S16,请 不要 在 草地 上 走 。,Please don't walk on the grass.,草
P1U02-S17,她的 英语 很 好 。,Her English is very good.,英
P1U02-S18,公园 里 的 花 都 开 了 。,The flowers in the park have all bloomed.,花
P1U02-S19,很多 中国人 喜欢 喝 绿茶 。,Many Chinese people like green tea.,茶
P1U02-S20,今年 的 收获 很 大 。,This year's harvest was big.,获
```

```csv
id,type,prompt,answer,options,note
P1U02-A01,error,春节是中国最重要的节目。,春节是中国最重要的节日。,,节目 = show; 节日 = holiday
P1U02-A02,error,我想喝一杯菜。,我想喝一杯茶。,,菜 and 茶 share 艹 on top
P1U02-A03,error,这个药很若。,这个药很苦。,,若 (ruò) has 右 under the grass
P1U02-A04,error,天空是篮色的。,天空是蓝色的。,,篮 (basket) has bamboo 竹 on top
P1U02-A05,error,我买了一斤平果。,我买了一斤苹果。,,Apple needs the grass radical
P1U02-A06,error,她每天化很多时间学英语。,她每天花很多时间学英语。,,化 is only the sound part
P1U02-A07,dialogue,你想喝什么？,我想喝茶。,我想喝茶。 / 我想吃药。 / 春节快乐！ / 天空是蓝色的。,
P1U02-A08,dialogue,我感冒了。,你吃药了吗？,你吃药了吗？ / 我们点菜吧。 / 草地很绿。 / 我喜欢花。,
P1U02-A09,dialogue,服务员，我们要点菜。,好的，你们想吃什么？,"好的，你们想吃什么？ / 不客气。 / 我买了花。 / 这个药很苦。",
P1U02-A10,dialogue,你工作太辛苦了。,没关系，我不累。,"没关系，我不累。 / 飞机降落了。 / 我喜欢绿茶。 / 他获得了第一名。",
```

```text
春节快到了。妈妈去花店买了很多红花，爸爸去市场买了苹果和很多菜。奶奶在家里做饭，我在旁边帮她。我们一家人一起喝茶、吃饭、看电视节目。春节是我最喜欢的节日。
```

```csv
id,question,answer,options
P1U02-R01,妈妈买了什么？,花,花 / 茶 / 药 / 苹果
P1U02-R02,爸爸在哪儿买了苹果和菜？,市场,市场 / 花店 / 药店 / 学校
P1U02-R03,奶奶在做什么？,做饭,做饭 / 喝茶 / 看电视 / 买花
P1U02-R04,“我”最喜欢的节日是什么？,春节,春节 / 中秋节 / 生日 / 新年
```

## P1-U03 扌 hand

```csv
zh,py,en,radical,component,words,lookalikes
打,dǎ,hit; play; make (a call),扌,丁,"打电话/dǎ diànhuà/make a call; 打扫/dǎsǎo/clean up",丁 灯 钉
找,zhǎo,look for,扌,戈,"找到/zhǎodào/find; 找钱/zhǎoqián/give change",我 戈 伐
把,bǎ,hold; (object marker),扌,巴,"把握/bǎwò/grasp; 一把椅子/yì bǎ yǐzi/a chair",巴 吧 爸
拉,lā,pull,扌,立,"拉开/lākāi/pull open; 拉手/lāshǒu/hold hands",立 位 垃
推,tuī,push,扌,隹,"推开/tuīkāi/push open; 推荐/tuījiàn/recommend",谁 准 堆
抱,bào,hug; hold,扌,包,"拥抱/yōngbào/hug; 抱歉/bàoqiàn/sorry",包 饱 跑
提,tí,lift; raise,扌,是,"提高/tígāo/improve; 提前/tíqián/in advance",是 题 堤
换,huàn,change; exchange,扌,奂,"换钱/huànqián/exchange money; 交换/jiāohuàn/swap",唤 焕
接,jiē,receive; pick up,扌,妾,"接电话/jiē diànhuà/answer the phone; 接受/jiēshòu/accept",妾 按
挂,guà,hang,扌,圭,"挂号/guàhào/register (hospital); 挂电话/guà diànhuà/hang up",圭 鞋 街
指,zhǐ,finger; point,扌,旨,"手指/shǒuzhǐ/finger; 指出/zhǐchū/point out",旨 脂
拍,pāi,clap; take (a photo),扌,白,"拍照/pāizhào/take a photo; 拍手/pāishǒu/clap",白 怕 伯
```

```csv
id,tokens,en,targets
P1U03-S01,请 帮 我 把 门 推开 。,Please help me push the door open.,把 推
P1U03-S02,我 找了 半天 ， 终于 找到 钥匙 了 。,"I looked for ages, and finally found the keys.",找
P1U03-S03,你 能 帮 我们 拍 张 照 吗 ？,Could you take a photo of us?,拍
P1U03-S04,抱歉 ， 我 来晚了 。,"Sorry, I'm late.",抱
P1U03-S05,我 想 提高 我的 汉语 水平 。,I want to improve my Chinese.,提
P1U03-S06,他 在 打电话 ， 你 等 一下 。,"He's on the phone, wait a moment.",打
P1U03-S07,飞机 几点 到 ？ 我 去 机场 接 你 。,What time does the plane land? I'll pick you up at the airport.,接
P1U03-S08,把 你的 衣服 挂 在 这儿 吧 。,Hang your clothes here.,把 挂
P1U03-S09,在 中国 看病 要 先 挂号 。,"In China, you register first to see a doctor.",挂
P1U03-S10,这儿 可以 换钱 吗 ？,Can I exchange money here?,换
P1U03-S11,请 把 门 拉开 。,Please pull the door open.,把 拉
P1U03-S12,妈妈 抱着 孩子 。,Mom is holding the child.,抱
P1U03-S13,他 用 手指 指了指 那个 人 。,He pointed at that person with his finger.,指
P1U03-S14,周末 我 在家 打扫 房间 。,On weekends I clean my room.,打
P1U03-S15,老板 ， 你 还没 找 我 钱 呢 。,"Boss, you haven't given me my change yet.",找
P1U03-S16,他的 电话 我 没 接到 。,I missed his phone call.,接
P1U03-S17,你 可以 给 我 推荐 一个 饭馆 吗 ？,Can you recommend a restaurant?,推
P1U03-S18,大家 都 拍手 欢迎 他 。,Everyone clapped to welcome him.,拍
P1U03-S19,我们 提前 十分钟 到 吧 。,Let's arrive ten minutes early.,提
P1U03-S20,这件 衣服 太 大 了 ， 能 换 一件 吗 ？,"This is too big, can I exchange it?",换
```

```csv
id,type,prompt,answer,options,note
P1U03-A01,error,请帮我把门谁开。,请帮我把门推开。,,谁 has 讠; push needs 扌
P1U03-A02,error,他在钉电话。,他在打电话。,,钉 (nail) has 钅
P1U03-A03,error,我们一起怕张照吧。,我们一起拍张照吧。,,怕 (afraid) has 忄
P1U03-A04,error,我想题高我的汉语水平。,我想提高我的汉语水平。,,题 = topic
P1U03-A05,error,饱歉，我来晚了。,抱歉，我来晚了。,,饱 (full) has 饣
P1U03-A06,error,我去机场按你。,我去机场接你。,,按 = press
P1U03-A07,dialogue,你能帮我们拍张照吗？,没问题。,没问题。 / 我在打电话。 / 门推不开。 / 我没找到。,
P1U03-A08,dialogue,喂，我到机场了。,我马上去接你。,我马上去接你。 / 我在挂号。 / 请换钱。 / 大家都拍手。,
P1U03-A09,dialogue,这件衣服太大了。,我给你换一件小的吧。,我给你换一件小的吧。 / 请推门。 / 他在打扫。 / 我没接电话。,
P1U03-A10,dialogue,你的钥匙找到了吗？,还没找到。,还没找到。 / 我把门拉开了。 / 我们提前到吧。 / 大家都拍手。,
```

```text
今天早上，我去机场接我的朋友小王。飞机晚了一个小时，我在机场找了一个咖啡馆，一边喝咖啡一边等。小王出来以后，我们拥抱了一下。他说：“抱歉，让你等了这么长时间。”我说：“没关系！”然后我们在机场门口拍了一张照片。
```

```csv
id,question,answer,options
P1U03-R01,“我”去机场做什么？,接朋友,接朋友 / 换钱 / 打电话 / 买咖啡
P1U03-R02,飞机晚了多长时间？,一个小时,一个小时 / 十分钟 / 半天 / 两个小时
P1U03-R03,小王为什么说“抱歉”？,让我等了很长时间,让我等了很长时间 / 他没拍照 / 他找不到钥匙 / 他不喝咖啡
P1U03-R04,他们在哪儿拍了照片？,机场门口,机场门口 / 咖啡馆里 / 飞机上 / 家里
```

## P1-U04 口 mouth

```csv
zh,py,en,radical,component,words,lookalikes
吃,chī,eat,口,乞,"吃饭/chīfàn/eat a meal; 小吃/xiǎochī/snacks",乞 气 吹
喝,hē,drink,口,曷,"喝水/hē shuǐ/drink water; 喝茶/hē chá/drink tea",渴 喊 歇
唱,chàng,sing,口,昌,"唱歌/chànggē/sing; 合唱/héchàng/chorus",昌 倡
叫,jiào,call; be named,口,丩,"叫做/jiàozuò/be called; 叫车/jiào chē/call a car",收 叶
吗,ma,(yes/no question),口,马,"好吗/hǎo ma/OK?",马 妈 骂
吧,ba,(suggestion),口,巴,"走吧/zǒu ba/let's go",巴 把 爸
呢,ne,(and you?),口,尼,"你呢/nǐ ne/and you?",尼 泥 妮
听,tīng,listen,口,斤,"听说/tīngshuō/hear that; 好听/hǎotīng/pleasant to hear",斤 近 所
咖,kā,(coffee),口,加,"咖啡/kāfēi/coffee",加 架 驾
啡,fēi,(coffee),口,非,"咖啡馆/kāfēiguǎn/café",非 排 悲
哭,kū,cry,口,犬,"哭了/kū le/cried; 别哭/bié kū/don't cry",笑 器
问,wèn,ask,口,门,"问题/wèntí/question; 请问/qǐngwèn/excuse me",门 们 间 闻
```

```csv
id,tokens,en,targets
P1U04-S01,请问 ， 这儿 附近 有 咖啡馆 吗 ？,"Excuse me, is there a café near here?",问 咖 啡 吗
P1U04-S02,我 听说 他 下个月 要 去 北京 。,I heard he's going to Beijing next month.,听
P1U04-S03,这首歌 很 好听 ， 你 会 唱 吗 ？,"This song sounds great, can you sing it?",听 唱 吗
P1U04-S04,你 叫 什么 名字 ？,What's your name?,叫
P1U04-S05,小孩子 饿 了 就 会 哭 。,Little kids cry when they're hungry.,哭
P1U04-S06,有 问题 就 问 老师 吧 。,"If you have a question, ask the teacher.",问 吧
P1U04-S07,你 喝 茶 还是 喝 咖啡 ？,Do you drink tea or coffee?,喝 咖 啡
P1U04-S08,我们 一起 去 吃饭 吧 。,Let's go eat together.,吃 吧
P1U04-S09,我 很 好 ， 你 呢 ？,"I'm good, and you?",呢
P1U04-S10,我 渴 了 ， 想 喝 水 。,"I'm thirsty, I want some water.",喝
P1U04-S11,你 喜欢 吃 中国 小吃 吗 ？,Do you like Chinese snacks?,吃 吗
P1U04-S12,她 唱歌 唱得 很 好听 。,She sings beautifully.,唱 听
P1U04-S13,我们 叫 个 车 去 机场 吧 。,Let's call a car to the airport.,叫 吧
P1U04-S14,别 哭 了 ， 没 什么 大 问题 。,"Don't cry, it's no big problem.",哭 问
P1U04-S15,你 听得懂 我 说 的 话 吗 ？,Can you understand what I'm saying?,听 吗
P1U04-S16,这个 菜 叫 什么 ？,What's this dish called?,叫
P1U04-S17,我 早上 喝 一杯 咖啡 。,I drink a cup of coffee in the morning.,喝 咖 啡
P1U04-S18,你 在 做 什么 呢 ？,What are you doing?,呢
P1U04-S19,晚上 我们 去 唱歌 吧 ！,Let's go sing tonight!,唱 吧
P1U04-S20,我 想 问 你 一个 问题 。,I want to ask you a question.,问
```

```csv
id,type,prompt,answer,options,note
P1U04-A01,error,我渴了，想渴水。,我渴了，想喝水。,,渴 (thirsty) has 氵; drink has 口
P1U04-A02,error,你叫什么名字吗？,你叫什么名字？,,No 吗 with a question word
P1U04-A03,error,我很好，你吗？,我很好，你呢？,,"""And you?"" is 呢"
P1U04-A04,error,有问题就闻老师吧。,有问题就问老师吧。,,闻 (smell) has 耳 inside 门
P1U04-A05,error,我想吃一杯咖啡。,我想喝一杯咖啡。,,You drink (喝) coffee
P1U04-A06,error,我们一起去吃饭吗！,我们一起去吃饭吧！,,A suggestion takes 吧
P1U04-A07,dialogue,你好吗？,我很好，你呢？,我很好，你呢？ / 我叫小明。 / 我们走吧。 / 别哭了。,
P1U04-A08,dialogue,你喝什么？,我喝咖啡。,我喝咖啡。 / 我吃饭了。 / 他在唱歌。 / 请问。,
P1U04-A09,dialogue,请问，咖啡馆在哪儿？,就在前面。,就在前面。 / 我不喝茶。 / 我叫王明。 / 好听吗？,
P1U04-A10,dialogue,我们去唱歌吧！,好啊，走吧！,好啊，走吧！ / 你叫什么？ / 我没问题。 / 他哭了。,
```

```text
星期六晚上，我和朋友们去唱歌。小李唱歌很好听，大家都叫她“歌星”。唱完歌，我们都饿了，就去吃小吃。我问小李：“你想吃什么？”她说：“我想喝一杯咖啡，吃一点儿小吃。”那天我们都很高兴。
```

```csv
id,question,answer,options
P1U04-R01,他们星期六晚上做什么？,唱歌,唱歌 / 喝茶 / 上课 / 看电影
P1U04-R02,大家叫小李什么？,歌星,歌星 / 老师 / 小明 / 朋友
P1U04-R03,唱完歌他们怎么了？,饿了,饿了 / 哭了 / 渴了 / 累了
P1U04-R04,小李想喝什么？,咖啡,咖啡 / 茶 / 水 / 酒
```

## P1-U05 亻 person

```csv
zh,py,en,radical,component,words,lookalikes
们,men,(plural),亻,门,"我们/wǒmen/we; 人们/rénmen/people",门 问 闷
住,zhù,live; stay,亻,主,"住在/zhù zài/live in; 记住/jìzhù/remember",主 注 往
做,zuò,do; make,亻,故,"做饭/zuòfàn/cook; 做作业/zuò zuòyè/do homework",故 作
体,tǐ,body,亻,本,"身体/shēntǐ/body; health; 体育/tǐyù/sports",本 休
休,xiū,rest,亻,木,"休息/xiūxi/rest; 退休/tuìxiū/retire",体 林
信,xìn,trust; letter,亻,言,"相信/xiāngxìn/believe; 信用卡/xìnyòngkǎ/credit card",言 话
但,dàn,but,亻,旦,"但是/dànshì/but; 不但/búdàn/not only",旦 担 胆
位,wèi,seat; (polite measure word),亻,立,"座位/zuòwèi/seat; 一位老师/yí wèi lǎoshī/a teacher",立 拉 泣
件,jiàn,(measure word for items),亻,牛,"一件衣服/yí jiàn yīfu/a piece of clothing; 文件/wénjiàn/document",牛 伴
便,biàn / pián,convenient / cheap,亻,更,"方便/fāngbiàn/convenient; 便宜/piányi/cheap",更 硬
借,jiè,borrow; lend,亻,昔,"借书/jiè shū/borrow a book; 借钱/jiè qián/borrow money",昔 错 惜
像,xiàng,resemble,亻,象,"好像/hǎoxiàng/seem; 像…一样/xiàng…yíyàng/just like",象 橡
```

```csv
id,tokens,en,targets
P1U05-S01,你 住在 哪儿 ？,Where do you live?,住
P1U05-S02,我 身体 不 太 舒服 ， 想 休息 一天 。,"I don't feel well, I want to rest for a day.",体 休
P1U05-S03,这家 店 的 东西 又 便宜 又 好 。,This shop's things are cheap and good.,便
P1U05-S04,我 可以 借 你的 笔 用 一下 吗 ？,Can I borrow your pen for a moment?,借
P1U05-S05,他 长得 很 像 他 爸爸 。,He looks a lot like his dad.,像
P1U05-S06,我 相信 你 一定 能 做到 。,I believe you can do it.,信 做
P1U05-S07,这件 衣服 很 漂亮 ， 但是 太 贵 了 。,"This piece of clothing is pretty, but too expensive.",件 但
P1U05-S08,请问 ， 这个 座位 有 人 吗 ？,"Excuse me, is this seat taken?",位
P1U05-S09,可以 用 信用卡 吗 ？,Can I use a credit card?,信
P1U05-S10,我们 休息 一下 吧 。,Let's rest for a moment.,们 休
P1U05-S11,我 每天 晚上 做饭 。,I cook every evening.,做
P1U05-S12,住在 这儿 很 方便 。,Living here is very convenient.,住 便
P1U05-S13,你 好像 不 太 高兴 。,You seem a bit unhappy.,像
P1U05-S14,他 不但 会 说 汉语 ， 还 会 写 汉字 。,"He can not only speak Chinese, but also write characters.",但
P1U05-S15,我 爷爷 去年 退休 了 。,My grandpa retired last year.,休
P1U05-S16,这 位 是 我们 的 新 老师 。,This is our new teacher.,位 们
P1U05-S17,我 想 去 图书馆 借 几本 书 。,I want to borrow some books from the library.,借
P1U05-S18,多 运动 对 身体 好 。,Exercise is good for your health.,体
P1U05-S19,他 给 妈妈 写了 一封 信 。,He wrote a letter to his mom.,信
P1U05-S20,我的 作业 还 没 做完 。,I haven't finished my homework yet.,做
```

```csv
id,type,prompt,answer,options,note
P1U05-A01,error,你注在哪儿？,你住在哪儿？,,注 has 氵; living is what people do (亻)
P1U05-A02,error,我身休不太舒服。,我身体不太舒服。,,休 (rest) and 体 (body) differ by one stroke
P1U05-A03,error,这家店的东西很更宜。,这家店的东西很便宜。,,更 is only the sound part
P1U05-A04,error,我可以错你的笔吗？,我可以借你的笔吗？,,错 (wrong) has 钅
P1U05-A05,error,他长得很象他爸爸。,他长得很像他爸爸。,,象 = elephant; resemble needs 亻
P1U05-A06,error,我门是好朋友。,我们是好朋友。,,门 = door; the plural adds 亻
P1U05-A07,dialogue,请问，这个座位有人吗？,没有，你坐吧。,"没有，你坐吧。 / 我住在北京。 / 我借了一本书。 / 他像爸爸。",
P1U05-A08,dialogue,你住在哪儿？,我住在学校旁边。,我住在学校旁边。 / 我在休息。 / 太便宜了。 / 我相信你。,
P1U05-A09,dialogue,我可以借你的笔用一下吗？,当然可以。,当然可以。 / 我身体很好。 / 这件太贵了。 / 我们走吧。,
P1U05-A10,dialogue,你今天怎么了？,我身体不太舒服。,我身体不太舒服。 / 我住在五楼。 / 可以用信用卡。 / 这位是老师。,
```

```text
我住在学校旁边，去上课很方便。我们学校的图书馆很大，我常常去那儿借书。上个星期我身体不太舒服，在家休息了三天。我的同学小张给我送来了作业，还给我做了一碗汤。我相信，她是我最好的朋友。
```

```csv
id,question,answer,options
P1U05-R01,“我”住在哪儿？,学校旁边,学校旁边 / 图书馆里 / 小张家 / 医院旁边
P1U05-R02,“我”常常去图书馆做什么？,借书,借书 / 做饭 / 休息 / 上课
P1U05-R03,“我”在家休息了几天？,三天,三天 / 一天 / 两天 / 一个星期
P1U05-R04,小张给“我”做了什么？,一碗汤,一碗汤 / 一本书 / 一封信 / 一件衣服
```

## P1-U06 讠 speech

```csv
zh,py,en,radical,component,words,lookalikes
说,shuō,speak,讠,兑,"说话/shuōhuà/speak; 小说/xiǎoshuō/novel",兑 税 脱
话,huà,words; speech,讠,舌,"电话/diànhuà/phone; 普通话/pǔtōnghuà/Mandarin",舌 活 适
请,qǐng,please; invite,讠,青,"请客/qǐngkè/treat (pay for others); 请假/qǐngjià/ask for leave",清 情 晴 青
谢,xiè,thank,讠,射,"谢谢/xièxie/thank you; 感谢/gǎnxiè/be grateful",射 树
认,rèn,recognize,讠,人,"认识/rènshi/know (a person); 认真/rènzhēn/serious",人 队 从
识,shí,know,讠,只,"知识/zhīshi/knowledge; 常识/chángshí/common sense",只 织 职
语,yǔ,language,讠,吾,"语言/yǔyán/language; 汉语/Hànyǔ/Chinese",吾 悟
读,dú,read; study,讠,卖,"读书/dúshū/study; 阅读/yuèdú/reading",卖 买 续
课,kè,class; lesson,讠,果,"上课/shàngkè/go to class; 课本/kèběn/textbook",果 棵 颗
词,cí,word,讠,司,"生词/shēngcí/new word; 词典/cídiǎn/dictionary",司 同
试,shì,try; test,讠,式,"考试/kǎoshì/exam; 试试/shìshi/give it a try",式 拭
记,jì,remember; record,讠,己,"记住/jìzhù/memorize; 日记/rìjì/diary; 忘记/wàngjì/forget",己 纪 起
```

```csv
id,tokens,en,targets
P1U06-S01,很 高兴 认识 你 。,Nice to meet you.,认 识
P1U06-S02,他 学习 很 认真 ， 每天 都 读书 。,"He studies seriously, and reads every day.",认 读
P1U06-S03,今天 晚上 我 请客 。,Tonight is my treat.,请
P1U06-S04,这个 生词 我 总是 记不住 。,I can never remember this new word.,词 记
P1U06-S05,明天 有 考试 ， 我 得 复习 课本 。,"There's an exam tomorrow, I have to review the textbook.",试 课
P1U06-S06,我 想 跟 老师 请 两天 假 。,I want to ask the teacher for two days off.,请
P1U06-S07,你 可以 试试 这件 衣服 。,You can try on this piece of clothing.,试
P1U06-S08,谢谢 你 告诉 我 。,Thank you for telling me.,谢
P1U06-S09,请 你 说 慢 一点儿 。,Please speak a little more slowly.,请 说
P1U06-S10,我 不 认识 这个 字 。,I don't know this character.,认 识
P1U06-S11,明天 几点 上课 ？,What time is class tomorrow?,课
P1U06-S12,汉语 不是 一门 很 难 的 语言 。,Chinese isn't a hard language.,语
P1U06-S13,我 每天 晚上 都 写 日记 。,I write in my diary every night.,记
P1U06-S14,你 会 说 普通话 吗 ？,Can you speak Mandarin?,说 话
P1U06-S15,有 不 认识 的 词 ， 就 查 词典 。,"If there's a word you don't know, look it up in the dictionary.",认 识 词
P1U06-S16,他 在 打 电话 ， 请 等 一下 。,"He's on the phone, please wait a moment.",话 请
P1U06-S17,读书 可以 让 人 学到 很多 知识 。,Reading lets you gain a lot of knowledge.,读 识
P1U06-S18,我 忘记 带 课本 了 。,I forgot to bring my textbook.,记 课
P1U06-S19,非常 感谢 你的 帮助 。,Thank you very much for your help.,谢
P1U06-S20,我 想 试试 用 汉语 说话 。,I want to try speaking in Chinese.,试 说 话
```

```csv
id,type,prompt,answer,options,note
P1U06-A01,error,很高兴认只你。,很高兴认识你。,,只 is only the sound part; know needs 讠
P1U06-A02,error,今天晚上我清客。,今天晚上我请客。,,Inviting is speech (讠) not water (氵)
P1U06-A03,error,树树你！,谢谢你！,,树 (tree) has 木; thank has 讠
P1U06-A04,error,明天有考式。,明天有考试。,,式 is only the sound part
P1U06-A05,error,这个生司我记不住。,这个生词我记不住。,,司 is only the sound part
P1U06-A06,error,我每天晚上都写日纪。,我每天晚上都写日记。,,纪 has 纟
P1U06-A07,dialogue,很高兴认识你。,我也很高兴认识你。,我也很高兴认识你。 / 不客气。 / 明天有考试。 / 我请客。,
P1U06-A08,dialogue,谢谢你！,不客气。,不客气。 / 我不认识他。 / 请说慢一点儿。 / 我记住了。,
P1U06-A09,dialogue,你会说汉语吗？,会一点儿。,会一点儿。 / 我在上课。 / 这是词典。 / 请试试。,
P1U06-A10,dialogue,这个字你认识吗？,不认识，我查一下词典。,"不认识，我查一下词典。 / 谢谢你告诉我。 / 今天我请客。 / 我在写日记。",
```

```text
我在北京的一个语言学校学汉语。每天上午我们有四节课。我们的老师很认真，说话也很清楚。下课以后，我常常去图书馆读书、查词典、记生词。晚上我用汉语写日记。下个星期有考试，我得好好复习。
```

```csv
id,question,answer,options
P1U06-R01,“我”在哪儿学汉语？,语言学校,语言学校 / 图书馆 / 公司 / 家里
P1U06-R02,每天上午有几节课？,四节,四节 / 两节 / 三节 / 五节
P1U06-R03,晚上“我”做什么？,写日记,写日记 / 上课 / 打电话 / 请客
P1U06-R04,下个星期有什么？,考试,考试 / 假期 / 新课本 / 生日
```

## P1-U07 木 tree

```csv
zh,py,en,radical,component,words,lookalikes
树,shù,tree,木,对,"树木/shùmù/trees; 树叶/shùyè/leaf",对 村
林,lín,woods,木,木,"树林/shùlín/grove; 森林/sēnlín/forest",森 材
森,sēn,forest,木,林,"森林/sēnlín/forest",林 淋
桌,zhuō,table,木,—,"桌子/zhuōzi/table; 书桌/shūzhuō/desk",卓 早
椅,yǐ,chair,木,奇,"椅子/yǐzi/chair",奇 骑 寄
杯,bēi,cup,木,不,"杯子/bēizi/cup; 一杯茶/yì bēi chá/a cup of tea",不 坏 怀
校,xiào,school,木,交,"学校/xuéxiào/school; 校长/xiàozhǎng/principal",交 较 饺
机,jī,machine,木,几,"手机/shǒujī/phone; 飞机/fēijī/plane; 机会/jīhuì/chance",几 饥 肌
楼,lóu,building; floor,木,娄,"楼上/lóushàng/upstairs; 楼梯/lóutī/stairs",娄 数 搂
板,bǎn,board,木,反,"老板/lǎobǎn/boss; 黑板/hēibǎn/blackboard",反 饭 版
果,guǒ,fruit; result,木,—,"水果/shuǐguǒ/fruit; 结果/jiéguǒ/result; 如果/rúguǒ/if",课 棵 颗
本,běn,root; (measure word for books),木,—,"本子/běnzi/notebook; 日本/Rìběn/Japan; 根本/gēnběn/at all",木 体 末
```

```csv
id,tokens,en,targets
P1U07-S01,我的 手机 在 桌子 上 。,My phone is on the table.,机 桌
P1U07-S02,学校 后面 有 一片 森林 。,There's a forest behind the school.,校 森 林
P1U07-S03,老板 ， 来 一杯 咖啡 。,"Boss, one coffee please.",板 杯
P1U07-S04,我 住在 五楼 ， 没有 电梯 。,"I live on the fifth floor, with no elevator.",楼
P1U07-S05,这 是 一个 很好 的 机会 。,This is a great opportunity.,机
P1U07-S06,结果 他 还是 没 来 。,In the end he still didn't come.,果
P1U07-S07,多 吃 水果 对 身体 好 。,Eating more fruit is good for you.,果
P1U07-S08,我 根本 不 认识 他 。,I don't know him at all.,本
P1U07-S09,学校 前面 有 一棵 大树 。,There's a big tree in front of the school.,校 树
P1U07-S10,我的 本子 在 哪儿 ？,Where is my notebook?,本
P1U07-S11,杯子 在 桌子 上 。,The cup is on the table.,杯 桌
P1U07-S12,老板 不 在 。,The boss isn't here.,板
P1U07-S13,请 坐 这把 椅子 。,Please sit in this chair.,椅
P1U07-S14,飞机 几点 起飞 ？,What time does the plane take off?,机
P1U07-S15,秋天 的 树叶 是 红色 的 。,Autumn leaves are red.,树
P1U07-S16,我家 楼下 有 一个 超市 。,There's a supermarket downstairs from my home.,楼
P1U07-S17,老师 在 黑板 上 写字 。,The teacher is writing on the blackboard.,板
P1U07-S18,如果 你 有 时间 ， 我们 一起 去 吧 。,"If you have time, let's go together.",果
P1U07-S19,我 买了 三本 书 。,I bought three books.,本
P1U07-S20,这个 学校 的 校长 很 年轻 。,This school's principal is very young.,校
```

```csv
id,type,prompt,answer,options,note
P1U07-A01,error,我的手几在桌子上。,我的手机在桌子上。,,几 is only the sound part
P1U07-A02,error,老饭，来一杯咖啡。,老板，来一杯咖啡。,,饭 has 饣; board has 木
P1U07-A03,error,我买了三体书。,我买了三本书。,,体 has 亻
P1U07-A04,error,学交前面有一棵大树。,学校前面有一棵大树。,,交 is only the sound part
P1U07-A05,error,我住在五数。,我住在五楼。,,数 (number) shares 娄 but has 攵
P1U07-A06,error,多吃水课对身体好。,多吃水果对身体好。,,课 (class) has 讠
P1U07-A07,dialogue,老板，来一杯咖啡。,好的，请等一下。,"好的，请等一下。 / 我住在五楼。 / 我的手机在桌子上。 / 结果他没来。",
P1U07-A08,dialogue,你的手机在哪儿？,在桌子上。,在桌子上。 / 我买了三本书。 / 树叶是红色的。 / 我不认识他。,
P1U07-A09,dialogue,你住几楼？,我住五楼。,我住五楼。 / 我喝一杯茶。 / 学校很大。 / 他是老板。,
P1U07-A10,dialogue,你喜欢吃水果吗？,喜欢，我每天都吃苹果。,"喜欢，我每天都吃苹果。 / 我坐这把椅子。 / 飞机八点起飞。 / 黑板上有字。",
```

```text
我们的学校不大，可是很漂亮。学校前面有很多树，后面有一片小森林。我们的教室在三楼，里面有三十张桌子和三十把椅子。老师每天在黑板上写很多字。下课以后，我喜欢在树下喝一杯茶，看一本书。
```

```csv
id,question,answer,options
P1U07-R01,学校后面有什么？,一片小森林,一片小森林 / 很多楼 / 一个超市 / 一条河
P1U07-R02,教室在几楼？,三楼,三楼 / 一楼 / 五楼 / 二楼
P1U07-R03,教室里有多少把椅子？,三十把,三十把 / 十三把 / 三把 / 二十把
P1U07-R04,下课以后“我”喜欢做什么？,在树下喝茶看书,在树下喝茶看书 / 在黑板上写字 / 去森林 / 打电话
```

## P1-U08 日 sun

```csv
zh,py,en,radical,component,words,lookalikes
明,míng,bright; tomorrow,日,月,"明天/míngtiān/tomorrow; 明白/míngbai/understand; 聪明/cōngming/clever",朋 名
早,zǎo,early; morning,日,十,"早上/zǎoshang/morning; 早饭/zǎofàn/breakfast",草 旱
晚,wǎn,late; evening,日,免,"晚上/wǎnshang/evening; 晚安/wǎn'ān/good night",免 挽 换
时,shí,time,日,寸,"时间/shíjiān/time; 小时/xiǎoshí/hour",对 讨 付
昨,zuó,yesterday,日,乍,"昨天/zuótiān/yesterday",作 怎 炸
晴,qíng,sunny,日,青,"晴天/qíngtiān/sunny day",请 情 清 睛
暖,nuǎn,warm,日,爰,"温暖/wēnnuǎn/warm; 暖和/nuǎnhuo/warm (weather)",缓 援
春,chūn,spring,日,—,"春天/chūntiān/spring; 春节/Chūnjié/Spring Festival",奏 泰
星,xīng,star,日,生,"星期/xīngqī/week; 明星/míngxīng/celebrity",生 性 姓
晨,chén,early morning,日,辰,"早晨/zǎochén/early morning",辰 震
景,jǐng,scenery,日,京,"风景/fēngjǐng/scenery; 背景/bèijǐng/background",京 凉 影
暗,àn,dark,日,音,"黑暗/hēi'àn/darkness",音 意 暖
```

```csv
id,tokens,en,targets
P1U08-S01,最近 天气 越来越 暖和 了 。,The weather is getting warmer lately.,暖
P1U08-S02,你 明白 我的 意思 吗 ？,Do you understand what I mean?,明
P1U08-S03,昨天 晚上 我 十一点 才 睡觉 。,Last night I didn't go to bed until eleven.,昨 晚
P1U08-S04,我 一个 星期 上 五天 班 。,I work five days a week.,星
P1U08-S05,这里 的 风景 太 美 了 。,The scenery here is beautiful.,景
P1U08-S06,房间 里 太 暗 了 ， 开灯 吧 。,"It's too dark in the room, turn on the light.",暗
P1U08-S07,明天 是 晴天 ， 我们 去 爬山 吧 。,"Tomorrow will be sunny, let's go hiking.",明 晴
P1U08-S08,你 昨天 几点 睡觉 ？,What time did you go to bed yesterday?,昨
P1U08-S09,我 没有 时间 。,I don't have time.,时
P1U08-S10,晚安 ！,Good night!,晚
P1U08-S11,春天 来 了 。,Spring has come.,春
P1U08-S12,我 每天 早上 七点 起床 。,I get up at seven every morning.,早
P1U08-S13,他 很 聪明 ， 学 什么 都 很快 。,"He's clever, he learns everything fast.",明
P1U08-S14,早晨 的 空气 很 好 。,The early-morning air is fresh.,晨
P1U08-S15,坐 飞机 要 三个 小时 。,The flight takes three hours.,时
P1U08-S16,今天 星期几 ？,What day of the week is it today?,星
P1U08-S17,你 吃 早饭 了 吗 ？,Have you had breakfast?,早
P1U08-S18,对不起 ， 我 来晚 了 。,"Sorry, I'm late.",晚
P1U08-S19,晚上 的 星星 很 亮 。,The stars are bright at night.,晚 星
P1U08-S20,春节 是 一个 温暖 的 节日 。,Spring Festival is a warm holiday.,春 暖
```

```csv
id,type,prompt,answer,options,note
P1U08-A01,error,你朋白我的意思吗？,你明白我的意思吗？,,朋 is two moons; bright is sun + moon
P1U08-A02,error,作天晚上我十一点才睡觉。,昨天晚上我十一点才睡觉。,,作 has 亻; days have 日
P1U08-A03,error,明天是请天。,明天是晴天。,,Sunny needs 日
P1U08-A04,error,我一个生期上五天班。,我一个星期上五天班。,,生 is only the sound part
P1U08-A05,error,这里的风京太美了。,这里的风景太美了。,,京 is only the sound part
P1U08-A06,error,房间里太音了。,房间里太暗了。,,音 is only the sound part
P1U08-A07,dialogue,今天天气怎么样？,是晴天，很暖和。,"是晴天，很暖和。 / 我没有时间。 / 晚安！ / 我明白了。",
P1U08-A08,dialogue,你明白了吗？,明白了，谢谢。,"明白了，谢谢。 / 今天星期三。 / 春天来了。 / 太暗了。",
P1U08-A09,dialogue,晚安！,晚安，明天见！,"晚安，明天见！ / 我吃早饭了。 / 风景很美。 / 三个小时。",
P1U08-A10,dialogue,你每天几点起床？,早上七点。,早上七点。 / 三个小时。 / 星期五。 / 春天来了。,
```

```text
春天来了，天气越来越暖和。昨天是星期天，也是一个晴天。早晨六点，我和爸爸去山上看日出。山上的风景很美。晚上，我们在外面看星星。爸爸说：“明天你还要上学，早点儿睡吧。”
```

```csv
id,question,answer,options
P1U08-R01,昨天是星期几？,星期天,星期天 / 星期一 / 星期六 / 星期三
P1U08-R02,他们早晨几点去山上？,六点,六点 / 七点 / 五点 / 八点
P1U08-R03,晚上他们做什么？,看星星,看星星 / 看日出 / 睡觉 / 上学
P1U08-R04,爸爸为什么让“我”早点儿睡？,明天要上学,明天要上学 / 天太暗了 / 明天下雨 / 他累了
```

## P1-U09 忄/心 heart

```csv
zh,py,en,radical,component,words,lookalikes
忙,máng,busy,忄,亡,"帮忙/bāngmáng/help; 忙碌/mánglù/busy",忘 亡 盲
快,kuài,fast; happy,忄,夬,"快乐/kuàilè/happy; 愉快/yúkuài/pleasant",块 决 筷
慢,màn,slow,忄,曼,"慢慢/mànmàn/slowly; 慢走/mànzǒu/take care",曼 馒 漫
情,qíng,feeling,忄,青,"事情/shìqing/matter; 心情/xīnqíng/mood; 感情/gǎnqíng/affection",请 清 晴
怕,pà,fear,忄,白,"害怕/hàipà/be scared; 恐怕/kǒngpà/I'm afraid that",拍 白 伯
懂,dǒng,understand,忄,董,"听懂/tīngdǒng/understand (by listening); 懂事/dǒngshì/sensible",董 重 动
惯,guàn,be used to,忄,贯,"习惯/xíguàn/habit; get used to",贯
想,xiǎng,think; want; miss,心,相,"想法/xiǎngfǎ/idea; 想家/xiǎngjiā/homesick",相 箱 湘
思,sī,think,心,田,"意思/yìsi/meaning; 有意思/yǒu yìsi/interesting",男 恩 田
感,gǎn,feel,心,咸,"感冒/gǎnmào/cold (illness); 感觉/gǎnjué/feel",咸 喊 减
忘,wàng,forget,心,亡,"忘记/wàngjì/forget; 难忘/nánwàng/unforgettable",忙 亡 望
急,jí,urgent; anxious,心,—,"着急/zháojí/worried; 急事/jíshì/urgent matter",怎 总
```

```csv
id,tokens,en,targets
P1U09-S01,我 最近 很 忙 ， 没 时间 去 看 你 。,"I've been busy lately, and haven't had time to visit you.",忙
P1U09-S02,你 说得 太 快 了 ， 请 说 慢 一点儿 。,"You're talking too fast, please speak more slowly.",快 慢
P1U09-S03,我 不 懂 这个 词 的 意思 。,I don't understand what this word means.,懂 思
P1U09-S04,你 习惯 这里 的 生活 了 吗 ？,Have you gotten used to life here?,惯
P1U09-S05,别 着急 ， 慢慢 来 。,"Don't worry, take your time.",急 慢
P1U09-S06,我 感冒 了 ， 感觉 很 不 舒服 。,I have a cold and feel awful.,感
P1U09-S07,我 怕 忘 了 ， 所以 写下来 了 。,"I was afraid I'd forget, so I wrote it down.",怕 忘
P1U09-S08,祝 你 生日 快乐 ！,Happy birthday!,快
P1U09-S09,我 很 想 家 。,I miss home a lot.,想
P1U09-S10,这个 电影 很 有意思 。,This movie is very interesting.,思
P1U09-S11,我 怕 狗 。,I'm afraid of dogs.,怕
P1U09-S12,你 怎么 想 ？,What do you think?,想
P1U09-S13,我 忘了 他的 名字 。,I forgot his name.,忘
P1U09-S14,你 能 帮 我 一个 忙 吗 ？,Can you do me a favor?,忙
P1U09-S15,他 今天 心情 不 太 好 。,He's not in a great mood today.,情
P1U09-S16,你 听懂 了 吗 ？,Did you understand (what you heard)?,懂
P1U09-S17,我 有 急事 ， 先 走 了 。,"I have something urgent, I'm heading off first.",急
P1U09-S18,快 下雨 了 ， 我们 快 走 吧 。,"It's about to rain, let's hurry.",快
P1U09-S19,学 汉字 是 一件 很 有意思 的 事情 。,Learning characters is a very interesting thing.,思 情
P1U09-S20,他 每天 早上 跑步 ， 已经 习惯 了 。,"He runs every morning, he's used to it now.",惯
```

```csv
id,type,prompt,answer,options,note
P1U09-A01,error,我最近很忘。,我最近很忙。,,Same parts: 忄 on the left = busy; 心 at the bottom = forget
P1U09-A02,error,我忙了他的名字。,我忘了他的名字。,,The reverse mistake
P1U09-A03,error,请说馒一点儿。,请说慢一点儿。,,馒 (bun) has 饣
P1U09-A04,error,我不董这个词的意思。,我不懂这个词的意思。,,董 is only the sound part
P1U09-A05,error,我拍狗。,我怕狗。,,拍 (clap) has 扌; fear has 忄
P1U09-A06,error,你习贯这里的生活了吗？,你习惯这里的生活了吗？,,贯 is only the sound part
P1U09-A07,dialogue,你最近怎么样？,很忙，可是很快乐。,"很忙，可是很快乐。 / 我怕狗。 / 别着急。 / 我忘了。",
P1U09-A08,dialogue,我听不懂。,我说慢一点儿。,我说慢一点儿。 / 生日快乐！ / 我很想家。 / 这个很有意思。,
P1U09-A09,dialogue,你感冒了吗？,是，我感觉很不舒服。,"是，我感觉很不舒服。 / 我很习惯。 / 他心情很好。 / 我有急事。",
P1U09-A10,dialogue,祝你生日快乐！,谢谢你！,谢谢你！ / 别着急。 / 慢走。 / 我不懂。,
```

```text
我来中国三个月了。刚来的时候，我听不懂中国人说话，因为他们说得太快了。我很想家，心情也不太好。现在我已经习惯了这里的生活，也交了很多朋友。学汉语虽然很忙，但是很有意思。我很快乐。
```

```csv
id,question,answer,options
P1U09-R01,“我”来中国多长时间了？,三个月,三个月 / 三年 / 三个星期 / 一个月
P1U09-R02,刚来的时候“我”为什么听不懂？,他们说得太快了,他们说得太快了 / 他们说得太慢了 / 我没有朋友 / 我感冒了
P1U09-R03,现在“我”怎么样？,习惯了这里的生活,习惯了这里的生活 / 很想家 / 心情不好 / 听不懂
P1U09-R04,学汉语怎么样？,很忙但是很有意思,很忙但是很有意思 / 很慢 / 没有意思 / 不忙
```

## P1-U10 女 woman

```csv
zh,py,en,radical,component,words,lookalikes
妈,mā,mom,女,马,"妈妈/māma/mom",马 吗 码
姐,jiě,older sister,女,且,"姐姐/jiějie/older sister; 小姐/xiǎojie/miss",且 组 租
妹,mèi,younger sister,女,未,"妹妹/mèimei/younger sister",未 味 末
奶,nǎi,milk; grandma,女,乃,"奶奶/nǎinai/grandma (dad's side); 牛奶/niúnǎi/milk",乃 扔 仍
她,tā,she,女,也,"她们/tāmen/they (female)",他 地 也
姓,xìng,surname,女,生,"姓名/xìngmíng/full name; 贵姓/guìxìng/your surname (polite)",性 星 生
始,shǐ,begin,女,台,"开始/kāishǐ/start",台 治 抬
婚,hūn,marriage,女,昏,"结婚/jiéhūn/marry; 离婚/líhūn/divorce",昏 混
要,yào,want; need,女,—,"需要/xūyào/need; 重要/zhòngyào/important",腰 票
妻,qī,wife,女,—,"妻子/qīzi/wife",凄 事
如,rú,if; like,女,口,"如果/rúguǒ/if; 比如/bǐrú/for example",加 知 和
娘,niáng,young woman,女,良,"姑娘/gūniang/girl; 新娘/xīnniáng/bride",良 狼 浪
```

```csv
id,tokens,en,targets
P1U10-S01,您 贵姓 ？ 我 姓 王 。,What's your surname? My surname is Wang.,姓
P1U10-S02,如果 明天 下雨 ， 我们 就 不 去 了 。,"If it rains tomorrow, we won't go.",如
P1U10-S03,他们 结婚 三年 了 。,They've been married three years.,婚
P1U10-S04,我 需要 一杯 牛奶 。,I need a glass of milk.,要 奶
P1U10-S05,电影 已经 开始 了 。,The movie has already started.,始
P1U10-S06,我 奶奶 今年 八十 岁 了 。,My grandma is eighty this year.,奶
P1U10-S07,这件 事 对 我 很 重要 。,This matters a lot to me.,要
P1U10-S08,她 是 一个 很 可爱 的 姑娘 。,She's a lovely girl.,她 娘
P1U10-S09,我 妹妹 十 岁 。,My younger sister is ten.,妹
P1U10-S10,奶奶 喜欢 喝 牛奶 。,Grandma likes to drink milk.,奶
P1U10-S11,什么 时候 开始 上课 ？,When does class start?,始
P1U10-S12,她 是 我 姐姐 。,She is my older sister.,她 姐
P1U10-S13,我 妈妈 是 医生 。,My mom is a doctor.,妈
P1U10-S14,他的 妻子 是 老师 。,His wife is a teacher.,妻
P1U10-S15,你 要 喝 什么 ？,What do you want to drink?,要
P1U10-S16,我 有 两个 姐姐 ， 一个 妹妹 。,"I have two older sisters, and one younger sister.",姐 妹
P1U10-S17,请 写 你的 姓名 。,Please write your full name.,姓
P1U10-S18,他们 下个月 结婚 。,They're getting married next month.,婚
P1U10-S19,我 喜欢 水果 ， 比如 苹果 和 香蕉 。,"I like fruit, for example apples and bananas.",如
P1U10-S20,小姐 ， 请问 洗手间 在 哪儿 ？,"Miss, excuse me, where's the restroom?",姐
```

```csv
id,type,prompt,answer,options,note
P1U10-A01,error,您贵性？,您贵姓？,,性 (nature) has 忄
P1U10-A02,error,电影已经开治了。,电影已经开始了。,,治 (govern) has 氵
P1U10-A03,error,他们结昏三年了。,他们结婚三年了。,,昏 is only the sound part
P1U10-A04,error,我味味十岁。,我妹妹十岁。,,味 (taste) has 口
P1U10-A05,error,加果明天下雨，我们就不去了。,如果明天下雨，我们就不去了。,,加 (add) has 力
P1U10-A06,error,她是一个很可爱的姑良。,她是一个很可爱的姑娘。,,良 is only the sound part
P1U10-A07,dialogue,您贵姓？,我姓王。,我姓王。 / 我要牛奶。 / 她是我妹妹。 / 电影开始了。,
P1U10-A08,dialogue,你有姐姐吗？,没有，我有一个妹妹。,"没有，我有一个妹妹。 / 电影开始了。 / 他们结婚了。 / 我需要牛奶。",
P1U10-A09,dialogue,电影几点开始？,晚上八点。,晚上八点。 / 她是姑娘。 / 我姓李。 / 很重要。,
P1U10-A10,dialogue,你要喝什么？,我要一杯牛奶。,我要一杯牛奶。 / 如果下雨。 / 我奶奶八十岁。 / 他们结婚了。,
```

```text
我家有五口人：爸爸、妈妈、奶奶、姐姐和我。我姐姐今年二十八岁，下个月就要结婚了。她的男朋友姓李，是一个医生。奶奶很高兴，她说：“你们结婚以后，要常常回家看看我。”
```

```csv
id,question,answer,options
P1U10-R01,“我”家有几口人？,五口,五口 / 四口 / 三口 / 六口
P1U10-R02,姐姐什么时候结婚？,下个月,下个月 / 明天 / 明年 / 下个星期
P1U10-R03,姐姐的男朋友姓什么？,李,李 / 王 / 张 / 马
P1U10-R04,奶奶希望他们做什么？,常常回家,常常回家 / 去北京 / 当医生 / 喝牛奶
```

## P1-U11 辶 walking

```csv
zh,py,en,radical,component,words,lookalikes
进,jìn,enter,辶,井,"进来/jìnlái/come in; 进步/jìnbù/progress",近 井 讲
远,yuǎn,far,辶,元,"永远/yǒngyuǎn/forever; 远处/yuǎnchù/the distance",元 园 运
近,jìn,near,辶,斤,"附近/fùjìn/nearby; 最近/zuìjìn/recently",进 斤 听
送,sòng,send; give,辶,关,"送给/sònggěi/give to; 送礼/sònglǐ/give a gift",关 达 迷
道,dào,road; way,辶,首,"知道/zhīdào/know; 道歉/dàoqiàn/apologize",首 导
过,guò,pass; (experience),辶,寸,"过来/guòlái/come over; 过去/guòqù/the past",边 对 寸
运,yùn,move; transport,辶,云,"运动/yùndòng/exercise; 运气/yùnqi/luck",云 远 会
迟,chí,late,辶,尺,"迟到/chídào/be late",尺 识 退
选,xuǎn,choose,辶,先,"选择/xuǎnzé/choose; choice",先 洗 远
通,tōng,through,辶,甬,"交通/jiāotōng/traffic; 通知/tōngzhī/notify",甬 痛 桶
边,biān,side,辶,力,"旁边/pángbiān/beside; 一边…一边/yìbiān…yìbiān/while",力 过 办
遇,yù,meet by chance,辶,禺,"遇到/yùdào/run into; 机遇/jīyù/opportunity",禺 偶 愚
```

```csv
id,tokens,en,targets
P1U11-S01,对不起 ， 我 迟到 了 。,"Sorry, I'm late.",迟
P1U11-S02,你 知道 附近 有没有 地铁站 ？,Do you know if there's a subway station nearby?,道 近
P1U11-S03,他的 汉语 进步 得 很快 。,His Chinese is improving fast.,进
P1U11-S04,我 想 送 她 一个 礼物 。,I want to give her a present.,送
P1U11-S05,我们 一边 吃饭 一边 聊天 。,We chatted while we ate.,边
P1U11-S06,今天 在 路上 遇到 了 一个 老 朋友 。,I ran into an old friend on the street today.,遇
P1U11-S07,多 运动 对 身体 好 。,Exercising more is good for you.,运
P1U11-S08,这 两个 你 选择 哪一个 ？,"Of these two, which do you choose?",选
P1U11-S09,请 进 。,Please come in.,进
P1U11-S10,远 吗 ？,Is it far?,远
P1U11-S11,附近 有 药店 吗 ？,Is there a pharmacy nearby?,近
P1U11-S12,我 去过 中国 。,I have been to China.,过
P1U11-S13,你 选 哪一个 ？,Which one do you choose?,选
P1U11-S14,我家 离 学校 很 近 。,My home is close to school.,近
P1U11-S15,这里 的 交通 很 方便 。,Getting around here is convenient.,通
P1U11-S16,我 永远 不会 忘记 你 。,I will never forget you.,远
P1U11-S17,他 坐 在 我 旁边 。,He's sitting next to me.,边
P1U11-S18,你 过来 一下 ， 我 有 事情 。,"Come over here, I need you for something.",过
P1U11-S19,老师 通知 我们 明天 考试 。,The teacher told us there's an exam tomorrow.,通
P1U11-S20,他 迟到 了 ， 所以 向 老师 道歉 。,"He was late, so he apologized to the teacher.",迟 道
```

```csv
id,type,prompt,answer,options,note
P1U11-A01,error,请近。,请进。,,近 (near) and 进 (enter) sound the same
P1U11-A02,error,我家离学校很进。,我家离学校很近。,,The reverse mistake
P1U11-A03,error,多远动对身体好。,多运动对身体好。,,远 = far; 运 = move
P1U11-A04,error,这两个你洗哪一个？,这两个你选哪一个？,,洗 (wash) has 氵
P1U11-A05,error,我们一边吃饭一力聊天。,我们一边吃饭一边聊天。,,力 is only the inside part
P1U11-A06,error,对不起，我尺到了。,对不起，我迟到了。,,尺 is only the sound part
P1U11-A07,dialogue,我可以进来吗？,请进。,请进。 / 很远。 / 我去过。 / 我迟到了。,
P1U11-A08,dialogue,你家离这儿远吗？,不远，很近。,"不远，很近。 / 我选这个。 / 交通很好。 / 我送你。",
P1U11-A09,dialogue,对不起，我迟到了。,没关系，进来吧。,"没关系，进来吧。 / 我知道。 / 太远了。 / 多运动。",
P1U11-A10,dialogue,你去过中国吗？,去过，去年去的。,"去过，去年去的。 / 我在旁边。 / 他进步很快。 / 我遇到了朋友。",
```

```text
我家离公司很远，坐地铁要一个小时。昨天早上地铁出了问题，我迟到了半个小时。我一进办公室，就向老板道歉。老板说：“没关系，交通不好，不是你的问题。”下班的时候，我在路上遇到了一个老同学，我们一边走一边聊天，很高兴。
```

```csv
id,question,answer,options
P1U11-R01,坐地铁去公司要多长时间？,一个小时,一个小时 / 半个小时 / 两个小时 / 十分钟
P1U11-R02,昨天“我”为什么迟到？,地铁出了问题,地铁出了问题 / 我起晚了 / 我生病了 / 我走错路了
P1U11-R03,老板说了什么？,没关系,没关系 / 你明天别来了 / 快点儿 / 你选择吧
P1U11-R04,下班的时候“我”遇到了谁？,一个老同学,一个老同学 / 老板 / 妈妈 / 老师
```

## P1-U12 宀 roof

```csv
zh,py,en,radical,component,words,lookalikes
家,jiā,home; family,宀,豕,"大家/dàjiā/everyone; 家人/jiārén/family",嫁 宝
字,zì,character,宀,子,"名字/míngzi/name; 汉字/Hànzì/Chinese characters",子 学 孩
安,ān,peace; safe,宀,女,"安全/ānquán/safe; 安静/ānjìng/quiet",女 按 案
室,shì,room,宀,至,"教室/jiàoshì/classroom; 办公室/bàngōngshì/office",至 到 屋
客,kè,guest,宀,各,"客人/kèrén/guest; 客气/kèqi/polite",各 路 落
定,dìng,fix; decide,宀,—,"一定/yídìng/definitely; 决定/juédìng/decide",走 足
完,wán,finish,宀,元,"完成/wánchéng/complete; 完全/wánquán/completely",元 玩 院
宝,bǎo,treasure,宀,玉,"宝宝/bǎobao/baby; 宝贝/bǎobèi/darling",玉 王 实
宿,sù,stay overnight,宀,—,"宿舍/sùshè/dormitory",缩 百
寄,jì,mail,宀,奇,"寄信/jì xìn/mail a letter; 邮寄/yóujì/send by post",奇 骑 椅
实,shí,real; solid,宀,—,"其实/qíshí/actually; 实在/shízài/really",宝 头 买
容,róng,contain,宀,谷,"容易/róngyì/easy; 内容/nèiróng/content",谷 客 溶
```

```csv
id,tokens,en,targets
P1U12-S01,图书馆 里 要 安静 。,You have to be quiet in the library.,安
P1U12-S02,不客气 ， 这 是 我 应该 做 的 。,"You're welcome, it's the least I could do.",客
P1U12-S03,我 决定 明年 去 中国 留学 。,I've decided to study abroad in China next year.,定
P1U12-S04,其实 学 汉字 没有 那么 难 。,"Actually, learning characters isn't that hard.",实 字
P1U12-S05,作业 你 写完 了 吗 ？,Have you finished your homework?,完
P1U12-S06,这个 包裹 寄到 上海 要 多少 钱 ？,How much does it cost to mail this package to Shanghai?,寄
P1U12-S07,他 住在 学校 的 宿舍 里 。,He lives in the school dorm.,宿
P1U12-S08,学 汉字 不 容易 ， 但是 很 有意思 。,"Learning characters isn't easy, but it's interesting.",字 容
P1U12-S09,欢迎 来 我家 。,Welcome to my home.,家
P1U12-S10,这个 字 怎么 写 ？,How do you write this character?,字
P1U12-S11,办公室 在 哪儿 ？,Where is the office?,室
P1U12-S12,其实 我 不 忙 。,"Actually, I'm not busy.",实
P1U12-S13,我 想 寄 一封 信 。,I want to mail a letter.,寄
P1U12-S14,今天 家里 来 了 很多 客人 。,Lots of guests came to our home today.,家 客
P1U12-S15,晚上 一个人 走路 不 安全 。,Walking alone at night isn't safe.,安
P1U12-S16,我 一定 会 来 的 。,I'll definitely come.,定
P1U12-S17,他们 的 宝宝 很 可爱 。,Their baby is very cute.,宝
P1U12-S18,这本 书 的 内容 很 有意思 。,This book's content is interesting.,容
P1U12-S19,大家 都 到 教室 了 吗 ？,Has everyone arrived at the classroom?,家 室
P1U12-S20,我 实在 太 累 了 。,I'm really too tired.,实
```

```csv
id,type,prompt,answer,options,note
P1U12-A01,error,图书馆里要按静。,图书馆里要安静。,,按 (press) has 扌
P1U12-A02,error,不各气。,不客气。,,Guest needs the roof 宀
P1U12-A03,error,作业你写元了吗？,作业你写完了吗？,,元 is only the sound part
P1U12-A04,error,学汉字不谷易。,学汉字不容易。,,谷 (valley) lacks the roof
P1U12-A05,error,我想骑一封信。,我想寄一封信。,,骑 (ride) has 马
P1U12-A06,error,我们的教至在三楼。,我们的教室在三楼。,,至 is only the sound part
P1U12-A07,dialogue,谢谢你！,不客气。,不客气。 / 我写完了。 / 我决定了。 / 很安静。,
P1U12-A08,dialogue,你的作业写完了吗？,还没写完。,还没写完。 / 欢迎来我家。 / 宝宝很可爱。 / 不安全。,
P1U12-A09,dialogue,你明天来吗？,一定来。,一定来。 / 我想寄信。 / 他住在宿舍。 / 其实很容易。,
P1U12-A10,dialogue,学汉字难吗？,其实不太难。,其实不太难。 / 大家好。 / 这是办公室。 / 不客气。,
```

```text
我叫大卫，现在住在大学的宿舍里。宿舍很安静，离教室也很近。上个星期，我决定给家人寄一个礼物。我在一张卡片上写了很多汉字。其实写汉字不容易，可是我一定要写完。妈妈收到以后，非常高兴。
```

```csv
id,question,answer,options
P1U12-R01,大卫住在哪儿？,大学的宿舍,大学的宿舍 / 家里 / 酒店 / 朋友家
P1U12-R02,宿舍怎么样？,很安静,很安静 / 很远 / 很贵 / 很吵
P1U12-R03,他给家人寄了什么？,礼物,礼物 / 信 / 钱 / 书
P1U12-R04,谁收到以后非常高兴？,妈妈,妈妈 / 爸爸 / 老师 / 朋友
```

## P1-U13 钅 metal

```csv
zh,py,en,radical,component,words,lookalikes
钱,qián,money,钅,戋,"钱包/qiánbāo/wallet; 多少钱/duōshao qián/how much",线 浅 践
银,yín,silver,钅,艮,"银行/yínháng/bank; 银色/yínsè/silver-colored",很 跟 眼
错,cuò,wrong,钅,昔,"不错/búcuò/not bad; 错误/cuòwù/mistake",借 昔 措
铁,tiě,iron,钅,失,"地铁/dìtiě/subway; 铁路/tiělù/railway",失 跌
钟,zhōng,clock; bell,钅,中,"分钟/fēnzhōng/minute; 钟表/zhōngbiǎo/clocks and watches",中 种 忠
针,zhēn,needle,钅,十,"打针/dǎzhēn/get an injection",十 计 汁
锻,duàn,forge,钅,段,"锻炼/duànliàn/work out",段 缎
链,liàn,chain,钅,连,"项链/xiàngliàn/necklace",连 莲
镜,jìng,mirror; lens,钅,竟,"眼镜/yǎnjìng/glasses; 镜子/jìngzi/mirror",竟 境 竞
锅,guō,pot,钅,呙,"火锅/huǒguō/hot pot",过 祸 窝
铅,qiān,lead (metal),钅,—,"铅笔/qiānbǐ/pencil",沿 船
钥,yào,key,钅,月,"钥匙/yàoshi/key",月 胡
```

```csv
id,tokens,en,targets
P1U13-S01,我的 钱包 和 钥匙 都 不见 了 。,My wallet and keys are both gone.,钱 钥
P1U13-S02,坐 地铁 去 机场 要 四十 分钟 。,It takes forty minutes to the airport by subway.,铁 钟
P1U13-S03,我 每天 早上 锻炼 一个 小时 。,I work out for an hour every morning.,锻
P1U13-S04,他 近视 ， 所以 要 戴 眼镜 。,"He's nearsighted, so he wears glasses.",镜
P1U13-S05,冬天 吃 火锅 最 舒服 了 。,Hot pot is the best thing to eat in winter.,锅
P1U13-S06,你 写得 不错 ， 可是 有 一个 小 错误 。,"You wrote it well, but there's one small mistake.",错
P1U13-S07,银行 几点 关门 ？,What time does the bank close?,银
P1U13-S08,医生 说 要 打针 。,The doctor says I need an injection.,针
P1U13-S09,我的 钥匙 丢 了 。,I lost my keys.,钥
P1U13-S10,等 五 分钟 。,Wait five minutes.,钟
P1U13-S11,你 说得 不错 。,What you said is quite right.,错
P1U13-S12,我 需要 一支 铅笔 。,I need a pencil.,铅
P1U13-S13,镜子 在 哪儿 ？,Where is the mirror?,镜
P1U13-S14,这个 多少 钱 ？,How much is this?,钱
P1U13-S15,她 戴着 一条 银 项链 。,She's wearing a silver necklace.,银 链
P1U13-S16,对不起 ， 是 我 错 了 。,"Sorry, I was wrong.",错
P1U13-S17,北京 的 地铁 很 方便 。,Beijing's subway is very convenient.,铁
P1U13-S18,你 吃过 四川 火锅 吗 ？,Have you ever had Sichuan hot pot?,锅
P1U13-S19,我 去 银行 取 钱 。,I'm going to the bank to withdraw money.,银 钱
P1U13-S20,多 锻炼 身体 ， 少 生病 。,"Work out more, get sick less.",锻
```

```csv
id,type,prompt,answer,options,note
P1U13-A01,error,我的线包不见了。,我的钱包不见了。,,线 (thread) has 纟
P1U13-A02,error,我去很行取钱。,我去银行取钱。,,很 has 彳; silver has 钅
P1U13-A03,error,对不起，是我借了。,对不起，是我错了。,,借 (borrow) has 亻
P1U13-A04,error,坐地失去机场。,坐地铁去机场。,,失 is only the right part
P1U13-A05,error,等五分中。,等五分钟。,,中 is only the sound part
P1U13-A06,error,他戴眼竟。,他戴眼镜。,,竟 is only the sound part
P1U13-A07,dialogue,这个多少钱？,二十块。,二十块。 / 我在锻炼。 / 银行关门了。 / 我戴眼镜。,
P1U13-A08,dialogue,你的钥匙找到了吗？,还没有，我的钱包也不见了。,"还没有，我的钱包也不见了。 / 坐地铁去吧。 / 我想吃火锅。 / 是我错了。",
P1U13-A09,dialogue,机场远吗？,坐地铁四十分钟。,坐地铁四十分钟。 / 医生说要打针。 / 我需要铅笔。 / 不错。,
P1U13-A10,dialogue,晚上吃什么？,我们去吃火锅吧！,我们去吃火锅吧！ / 银行几点开门？ / 镜子在这儿。 / 我锻炼了一个小时。,
```

```text
今天真倒霉！早上我去锻炼，回家的时候发现钥匙不见了。我在路上找了二十分钟，没找到。后来我去银行取钱，又发现钱包也不在了。最后，我在家门口的地上找到了钥匙和钱包。晚上我和朋友去吃火锅，心情好多了。
```

```csv
id,question,answer,options
P1U13-R01,早上“我”去做什么？,锻炼,锻炼 / 吃火锅 / 去银行 / 上班
P1U13-R02,“我”在路上找了多长时间？,二十分钟,二十分钟 / 两个小时 / 五分钟 / 四十分钟
P1U13-R03,钥匙和钱包在哪儿找到的？,家门口的地上,家门口的地上 / 银行里 / 地铁上 / 火锅店
P1U13-R04,晚上“我”做什么？,和朋友吃火锅,和朋友吃火锅 / 锻炼 / 去银行 / 打针
```

## P1-U14 纟 silk

```csv
zh,py,en,radical,component,words,lookalikes
红,hóng,red,纟,工,"红色/hóngsè/red; 红包/hóngbāo/red envelope",工 江 功
绿,lǜ,green,纟,录,"绿色/lǜsè/green; 绿茶/lǜchá/green tea",录 禄
级,jí,grade; level,纟,及,"年级/niánjí/school grade; 高级/gāojí/advanced",及 极 吸
给,gěi,give; for,纟,合,"给你/gěi nǐ/for you; 送给/sònggěi/give to",合 拾 恰
经,jīng,pass through,纟,—,"已经/yǐjīng/already; 经常/jīngcháng/often",轻 径
结,jié,tie; conclude,纟,吉,"结束/jiéshù/end; 结果/jiéguǒ/result",吉 洁
练,liàn,practice,纟,—,"练习/liànxí/practice; 训练/xùnliàn/training",炼 拣
纸,zhǐ,paper,纟,氏,"报纸/bàozhǐ/newspaper; 纸巾/zhǐjīn/tissue",氏 低 底
线,xiàn,line; thread,纟,戋,"路线/lùxiàn/route; 线上/xiànshàng/online",钱 浅
约,yuē,arrange; about,纟,勺,"约会/yuēhuì/date; 大约/dàyuē/approximately",药 的 钓
细,xì,thin; fine,纟,田,"仔细/zǐxì/careful; 详细/xiángxì/detailed",田 思 累
终,zhōng,end,纟,冬,"终于/zhōngyú/finally; 最终/zuìzhōng/ultimately",冬 钟 中
```

```csv
id,tokens,en,targets
P1U14-S01,我 已经 等 了 半个 小时 了 。,I've already waited half an hour.,经
P1U14-S02,春节 的 时候 长辈 会 给 孩子 红包 。,"At Spring Festival, elders give children red envelopes.",给 红
P1U14-S03,我 经常 跟 朋友 练习 说 汉语 。,I often practice speaking Chinese with friends.,经 练
P1U14-S04,他 终于 找到 了 工作 。,He finally found a job.,终
P1U14-S05,你 仔细 看看 ， 这 两个 字 有 什么 不 一样 ？,"Look carefully, how are these two characters different?",细
P1U14-S06,我们 约好 了 明天 下午 见面 。,We arranged to meet tomorrow afternoon.,约
P1U14-S07,会议 什么 时候 结束 ？,When does the meeting end?,结
P1U14-S08,这条 路线 的 交通 很 方便 。,Getting around on this route is very convenient.,线
P1U14-S09,我 喜欢 喝 绿茶 。,I like drinking green tea.,绿
P1U14-S10,给 我 吧 。,Give it to me.,给
P1U14-S11,我 每天 练习 写 汉字 。,I practice writing characters every day.,练
P1U14-S12,请 仔细 看 。,Please look carefully.,细
P1U14-S13,你 看 了 今天 的 报纸 吗 ？,Have you read today's newspaper?,纸
P1U14-S14,我 妹妹 上 三年级 。,My younger sister is in third grade.,级
P1U14-S15,从 这儿 到 机场 大约 要 一个 小时 。,It takes about an hour from here to the airport.,约
P1U14-S16,红灯 停 ， 绿灯 行 。,"Red light stop, green light go.",红 绿
P1U14-S17,这 是 我 送给 你 的 礼物 。,This is a gift I'm giving you.,给
P1U14-S18,考试 结果 出来 了 吗 ？,Are the exam results out?,结
P1U14-S19,我们 线上 见 吧 。,Let's meet online.,线
P1U14-S20,请 给 我 一张 纸 。,Please give me a sheet of paper.,给 纸
```

```csv
id,type,prompt,answer,options,note
P1U14-A01,error,我已轻等了半个小时了。,我已经等了半个小时了。,,轻 (light) has 车
P1U14-A02,error,他冬于找到了工作。,他终于找到了工作。,,冬 is only the sound part
P1U14-A03,error,我们药好了明天见面。,我们约好了明天见面。,,药 (medicine) has 艹 on top
P1U14-A04,error,请给我一张氏。,请给我一张纸。,,氏 is only the sound part
P1U14-A05,error,我每天炼习写汉字。,我每天练习写汉字。,,炼 (refine) has 火
P1U14-A06,error,会议什么时候吉束？,会议什么时候结束？,,吉 is only the sound part
P1U14-A07,dialogue,你经常练习汉语吗？,经常，我每天都练习。,"经常，我每天都练习。 / 我喜欢绿茶。 / 会议结束了。 / 给你。",
P1U14-A08,dialogue,我们什么时候见面？,我们约明天下午吧。,我们约明天下午吧。 / 他终于来了。 / 请仔细看。 / 这是报纸。,
P1U14-A09,dialogue,你等了多长时间了？,已经等了半个小时了。,已经等了半个小时了。 / 我上三年级。 / 红灯停。 / 线上见。,
P1U14-A10,dialogue,这两个字一样吗？,你仔细看看，不一样。,"你仔细看看，不一样。 / 给我吧。 / 我喝绿茶。 / 会议结束了。",
```

```text
春节的时候，爷爷奶奶给了我一个大红包。我很高兴，因为我已经等了一年了！我用红包里的钱买了一本练习本和很多彩色的纸。妹妹上三年级，她喜欢画画，我给了她一半的纸。她说：“谢谢哥哥！”
```

```csv
id,question,answer,options
P1U14-R01,谁给了“我”红包？,爷爷奶奶,爷爷奶奶 / 爸爸妈妈 / 老师 / 妹妹
P1U14-R02,“我”用钱买了什么？,练习本和纸,练习本和纸 / 绿茶 / 报纸 / 礼物
P1U14-R03,妹妹上几年级？,三年级,三年级 / 二年级 / 四年级 / 一年级
P1U14-R04,“我”给了妹妹什么？,一半的纸,一半的纸 / 红包 / 练习本 / 钱
```

## P1-U15 饣 food

```csv
zh,py,en,radical,component,words,lookalikes
饭,fàn,rice; meal,饣,反,"吃饭/chīfàn/eat; 米饭/mǐfàn/cooked rice; 饭店/fàndiàn/restaurant",反 板 版
饿,è,hungry,饣,我,"饿了/è le/hungry; 饿死了/è sǐ le/starving",我 俄 鹅
饱,bǎo,full (after eating),饣,包,"吃饱/chībǎo/eat one's fill",包 抱 跑
饺,jiǎo,dumpling,饣,交,"饺子/jiǎozi/dumplings; 包饺子/bāo jiǎozi/make dumplings",交 校 较
馆,guǎn,hall; restaurant,饣,官,"饭馆/fànguǎn/restaurant; 图书馆/túshūguǎn/library; 宾馆/bīnguǎn/hotel",官 管
饮,yǐn,drink,饣,欠,"饮料/yǐnliào/beverage; 饮食/yǐnshí/diet",欠 次 吹
饼,bǐng,flatbread; cake,饣,并,"月饼/yuèbing/mooncake; 饼干/bǐnggān/cookie",并 拼 瓶
馒,mán,steamed bun,饣,曼,"馒头/mántou/steamed bun",曼 慢 漫
饰,shì,decorate,饣,—,"装饰/zhuāngshì/decoration; 首饰/shǒushì/jewelry",师 布
馅,xiàn,filling,饣,—,"馅儿/xiànr/filling",陷 焰
饥,jī,starving,饣,几,"饥饿/jī'è/hunger",几 机 肌
餐,cān,meal,食,—,"餐厅/cāntīng/dining hall; 早餐/zǎocān/breakfast; 中餐/zhōngcān/Chinese food",食
```

```csv
id,tokens,en,targets
P1U15-S01,我 饿死 了 ， 我们 去 吃饭 吧 。,"I'm starving, let's go eat.",饿 饭
P1U15-S02,我 吃饱 了 ， 谢谢 。,"I'm full, thanks.",饱
P1U15-S03,中秋节 的 时候 大家 都 吃 月饼 。,Everyone eats mooncakes at Mid-Autumn Festival.,饼
P1U15-S04,你 想 喝 什么 饮料 ？,What would you like to drink?,饮
P1U15-S05,北方人 过年 喜欢 包 饺子 。,Northerners like to make dumplings at New Year.,饺
P1U15-S06,这家 饭馆 的 菜 又 便宜 又 好吃 。,The food at this restaurant is cheap and tasty.,饭 馆
P1U15-S07,你 喜欢 什么 馅儿 的 饺子 ？,What filling do you like in your dumplings?,馅 饺
P1U15-S08,图书馆 几点 开门 ？,What time does the library open?,馆
P1U15-S09,你 吃饭 了 吗 ？,Have you eaten?,饭
P1U15-S10,我 喜欢 吃 饺子 。,I like eating dumplings.,饺
P1U15-S11,餐厅 在 哪儿 ？,Where is the dining hall?,餐
P1U15-S12,我 不 饿 。,I'm not hungry.,饿
P1U15-S13,早上 我 吃 了 两个 馒头 。,I ate two steamed buns this morning.,馒
P1U15-S14,我们 今天 吃 中餐 还是 西餐 ？,Are we eating Chinese or Western food today?,餐
P1U15-S15,孩子 饿 了 ， 给 他 一块 饼干 吧 。,"The child is hungry, give him a cookie.",饿 饼
P1U15-S16,你 吃饱 了 吗 ？ 再 吃 一点儿 吧 。,Are you full? Have a bit more.,饱
P1U15-S17,宾馆 离 这儿 不 远 。,The hotel isn't far from here.,馆
P1U15-S18,健康 的 饮食 很 重要 。,A healthy diet is important.,饮
P1U15-S19,春节 的 时候 ， 家里 有 很多 装饰 。,"At Spring Festival, homes have lots of decorations.",饰
P1U15-S20,我们 在 学校 餐厅 吃 午饭 。,We eat lunch in the school dining hall.,餐 饭
```

```csv
id,type,prompt,answer,options,note
P1U15-A01,error,我俄死了。,我饿死了。,,俄 (Russia) has 亻
P1U15-A02,error,我吃抱了。,我吃饱了。,,抱 (hug) has 扌; full of food has 饣
P1U15-A03,error,北方人过年喜欢包校子。,北方人过年喜欢包饺子。,,校 (school) has 木
P1U15-A04,error,图书管几点开门？,图书馆几点开门？,,管 (manage) has bamboo 竹 on top
P1U15-A05,error,中秋节大家都吃月并。,中秋节大家都吃月饼。,,并 is only the sound part
P1U15-A06,error,早上我吃了两个慢头。,早上我吃了两个馒头。,,慢 (slow) has 忄
P1U15-A07,dialogue,你吃饭了吗？,还没吃，我好饿。,"还没吃，我好饿。 / 我吃了饼干。 / 图书馆开门了。 / 我喜欢装饰。",
P1U15-A08,dialogue,再吃一点儿吧！,不了，我吃饱了。,"不了，我吃饱了。 / 我很饿。 / 你想喝什么？ / 餐厅在哪儿？",
P1U15-A09,dialogue,你想喝什么饮料？,一杯绿茶。,一杯绿茶。 / 饺子。 / 馒头。 / 中餐。,
P1U15-A10,dialogue,你喜欢什么馅儿的饺子？,我喜欢白菜馅儿的。,我喜欢白菜馅儿的。 / 我吃饱了。 / 宾馆不远。 / 我不饿。,
```

```text
今天是春节，我们一家人在家里包饺子。妈妈做馅儿，爸爸和我包。奶奶说：“饺子要包得好看！”晚上我们吃了很多饺子，还吃了妈妈做的饼。吃完饭，大家都说：“太饱了！”我们一边喝饮料一边看电视，很开心。
```

```csv
id,question,answer,options
P1U15-R01,春节他们在家做什么？,包饺子,包饺子 / 做月饼 / 去饭馆 / 装饰家
P1U15-R02,谁做馅儿？,妈妈,妈妈 / 爸爸 / 奶奶 / 我
P1U15-R03,晚上除了饺子他们还吃了什么？,饼,饼 / 馒头 / 米饭 / 饼干
P1U15-R04,吃完饭大家说什么？,太饱了,太饱了 / 太饿了 / 不好吃 / 再吃一点儿
```

## P1-U16 贝 money

```csv
zh,py,en,radical,component,words,lookalikes
贵,guì,expensive; honored,贝,—,"太贵了/tài guì le/too expensive; 贵姓/guìxìng/your surname (polite)",贯 费
货,huò,goods,贝,化,"售货员/shòuhuòyuán/salesclerk; 发货/fāhuò/ship goods",化 花 华
购,gòu,buy,贝,勾,"购物/gòuwù/shopping; 网购/wǎnggòu/online shopping",沟 构
费,fèi,fee; spend,贝,弗,"免费/miǎnfèi/free; 费用/fèiyòng/cost",弗 佛 贵
账,zhàng,account; bill,贝,长,"结账/jiézhàng/pay the bill; 账户/zhànghù/account",张 长 胀
贴,tiē,stick; paste,贝,占,"贴纸/tiēzhǐ/sticker; 贴心/tiēxīn/thoughtful",占 站 点
资,zī,funds; resources,贝,次,"工资/gōngzī/salary; 资料/zīliào/materials",次 姿 咨
赚,zhuàn,earn,贝,兼,"赚钱/zhuànqián/make money",兼 嫌 谦
赛,sài,compete,贝,—,"比赛/bǐsài/match; competition",塞 寨
员,yuán,member; staff,贝,口,"服务员/fúwùyuán/waiter; 员工/yuángōng/employee",贝 圆 园
败,bài,lose; fail,贝,攵,"失败/shībài/failure; 打败/dǎbài/defeat",收 购
财,cái,wealth,贝,才,"发财/fācái/get rich; 财富/cáifù/wealth",才 材 团
```

```csv
id,tokens,en,targets
P1U16-S01,太 贵 了 ， 能 便宜 一点儿 吗 ？,"That's too expensive, can you go a bit lower?",贵
P1U16-S02,现在 很多 人 喜欢 网购 。,Lots of people like shopping online now.,购
P1U16-S03,服务员 ， 结账 ！,"Waiter, the bill please!",员 账
P1U16-S04,这个 博物馆 是 免费 的 。,This museum is free.,费
P1U16-S05,他的 工资 不 高 ， 可是 工作 很 有意思 。,"His pay isn't high, but the work is interesting.",资
P1U16-S06,失败 是 成功 之 母 。,Failure is the mother of success.,败
P1U16-S07,昨天 的 比赛 我们 赢 了 。,We won yesterday's match.,赛
P1U16-S08,新年 快乐 ， 恭喜 发财 ！,"Happy New Year, and may you prosper!",财
P1U16-S09,多少 钱 ？ 太 贵 了 。,How much is it? Too expensive.,贵
P1U16-S10,我 想 赚 更多 的 钱 。,I want to earn more money.,赚
P1U16-S11,是 免费 的 吗 ？,Is it free?,费
P1U16-S12,她 是 这家 商店 的 售货员 。,She's a salesclerk at this shop.,货 员
P1U16-S13,周末 我们 去 购物 吧 。,Let's go shopping this weekend.,购
P1U16-S14,我 在 手机 上 贴 了 一张 贴纸 。,I stuck a sticker on my phone.,贴
P1U16-S15,这次 失败 了 ， 下次 再 来 。,"Failed this time, try again next time.",败
P1U16-S16,你的 账户 里 还有 多少 钱 ？,How much money is left in your account?,账
P1U16-S17,他 一个月 能 赚 一万 块 。,He can earn ten thousand yuan a month.,赚
P1U16-S18,北京 的 东西 比较 贵 。,Things in Beijing are fairly expensive.,贵
P1U16-S19,这 是 公司 的 新 员工 。,This is the company's new employee.,员
P1U16-S20,你 看 了 昨天 的 足球 比赛 吗 ？,Did you watch yesterday's soccer match?,赛
```

```csv
id,type,prompt,answer,options,note
P1U16-A01,error,太费了，能便宜一点儿吗？,太贵了，能便宜一点儿吗？,,费 = fee; 贵 = expensive
P1U16-A02,error,这个博物馆是免贵的。,这个博物馆是免费的。,,The reverse mistake
P1U16-A03,error,服务员，结张！,服务员，结账！,,张 has 弓; a bill needs 贝
P1U16-A04,error,他的工次不高。,他的工资不高。,,次 is only the top part
P1U16-A05,error,新年快乐，恭喜发材！,新年快乐，恭喜发财！,,材 (material) has 木
P1U16-A06,error,现在很多人喜欢网沟。,现在很多人喜欢网购。,,沟 (ditch) has 氵
P1U16-A07,dialogue,这件衣服多少钱？,三百块。,三百块。 / 我赚钱了。 / 比赛开始了。 / 我是新员工。,
P1U16-A08,dialogue,太贵了，能便宜一点儿吗？,好吧，二百五十块。,"好吧，二百五十块。 / 恭喜发财！ / 是免费的。 / 我们赢了。",
P1U16-A09,dialogue,服务员，结账！,好的，一共八十块。,"好的，一共八十块。 / 欢迎光临。 / 我想购物。 / 失败了。",
P1U16-A10,dialogue,新年快乐！,新年快乐，恭喜发财！,"新年快乐，恭喜发财！ / 太贵了。 / 我们结账吧。 / 他赚了很多钱。",
```

```text
小王是一家商店的售货员，工资不高，可是他很喜欢这份工作。周末很多人来购物，商店里很忙。有一个客人说：“这件衣服太贵了，能便宜一点儿吗？”小王说：“今天买一件，送一张贴纸，是免费的！”客人很高兴，买了两件。
```

```csv
id,question,answer,options
P1U16-R01,小王做什么工作？,售货员,售货员 / 服务员 / 老师 / 老板
P1U16-R02,小王的工资怎么样？,不高,不高 / 很高 / 没有工资 / 不知道
P1U16-R03,客人觉得衣服怎么样？,太贵了,太贵了 / 太便宜了 / 太大了 / 很好看
P1U16-R04,客人买了几件？,两件,两件 / 一件 / 三件 / 没买
```

## P1-U17 look-alike radicals

```csv
zh,py,en,radical,component,words,lookalikes
冷,lěng,cold,冫,令,"冷水/lěngshuǐ/cold water; 很冷/hěn lěng/very cold",泠 令 铃
冰,bīng,ice,冫,水,"冰水/bīngshuǐ/ice water; 冰箱/bīngxiāng/fridge",水 永 冻
冬,dōng,winter,冫,—,"冬天/dōngtiān/winter",各 终
凉,liáng,cool,冫,京,"凉快/liángkuai/pleasantly cool",京 晾 谅
决,jué,decide,冫,夬,"决定/juédìng/decide",快 块 缺
次,cì,time (occurrence),冫,欠,"第一次/dì-yī cì/the first time; 这次/zhè cì/this time",欠 饮 吹
礼,lǐ,gift; ritual,礻,乚,"礼物/lǐwù/gift; 婚礼/hūnlǐ/wedding",扎 视
祝,zhù,wish,礻,兄,"祝你生日快乐/zhù nǐ shēngrì kuàilè/happy birthday",兄 说 况
福,fú,blessing,礻,畐,"幸福/xìngfú/happiness; 祝福/zhùfú/blessing",富 副 幅
神,shén,god; spirit,礻,申,"精神/jīngshen/energy; 神奇/shénqí/magical",申 伸 审
衫,shān,shirt,衤,彡,"衬衫/chènshān/shirt",杉 形
裤,kù,trousers,衤,库,"裤子/kùzi/trousers",库 酷
袜,wà,sock,衤,末,"袜子/wàzi/socks",末 抹 沫
被,bèi,quilt; (passive marker),衤,皮,"被子/bèizi/quilt; 被打/bèi dǎ/be hit",皮 波 破
脸,liǎn,face,月 (flesh),佥,"洗脸/xǐliǎn/wash one's face; 脸色/liǎnsè/complexion",险 检 验
脚,jiǎo,foot,月 (flesh),却,"脚步/jiǎobù/footstep",却 脑
腿,tuǐ,leg,月 (flesh),退,"大腿/dàtuǐ/thigh",退 褪
最,zuì,most,曰,取,"最好/zuìhǎo/best; 最近/zuìjìn/recently",取 聚 量
```

```csv
id,tokens,en,targets
P1U17-S01,今天 很 冷 ， 外面 都 结冰 了 。,"It's cold today, everything outside has frozen.",冷 冰
P1U17-S02,祝 你 生日 快乐 ， 天天 幸福 ！,"Happy birthday, I wish you happiness every day!",祝 福
P1U17-S03,我 买 了 一件 衬衫 和 一条 裤子 。,I bought a shirt and a pair of trousers.,衫 裤
P1U17-S04,这 是 我 最 喜欢 的 电视 节目 。,This is my favorite TV show.,最
P1U17-S05,你的 脸 怎么 红 了 ？,Why has your face gone red?,脸
P1U17-S06,这 是 我 第一次 来 中国 。,This is my first time in China.,次
P1U17-S07,我 走 了 一天 ， 腿 和 脚 都 很 疼 。,"I walked all day, my legs and feet hurt.",腿 脚
P1U17-S08,秋天 很 凉快 。,Autumn is pleasantly cool.,凉
P1U17-S09,我 决定 学 中文 。,I've decided to learn Chinese.,决
P1U17-S10,冬天 来 了 ， 多 穿 点儿 衣服 。,"Winter is here, wear more clothes.",冬
P1U17-S11,我 想 喝 一杯 冰水 。,I'd like a glass of ice water.,冰
P1U17-S12,这 是 送给 你 的 生日 礼物 。,This is a birthday present for you.,礼
P1U17-S13,他 今天 很 有 精神 。,He's full of energy today.,神
P1U17-S14,我的 袜子 在 哪儿 ？,Where are my socks?,袜
P1U17-S15,他 被 老师 批评 了 。,He was criticized by the teacher.,被
P1U17-S16,早上 起床 以后 先 洗脸 。,"After getting up, wash your face first.",脸
P1U17-S17,这次 考试 我 考得 最 好 。,I did best on this exam.,次 最
P1U17-S18,春节 的 时候 ， 大家 互相 祝福 。,"At Spring Festival, everyone exchanges blessings.",祝 福
P1U17-S19,冬天 晚上 要 盖 厚 被子 。,On winter nights you need a thick quilt.,冬 被
P1U17-S20,我的 脚 很 冷 ， 要 穿 袜子 。,"My feet are cold, I need to wear socks.",脚 冷 袜
```

```csv
id,type,prompt,answer,options,note
P1U17-A01,error,今天很泠。,今天很冷。,,泠 (líng) has three dots (氵); cold has two (冫)
P1U17-A02,error,我买了一件衬杉。,我买了一件衬衫。,,杉 (fir) has 木; shirt has 衤
P1U17-A03,error,祝你天天幸副！,祝你天天幸福！,,副 has 刂; blessing has 礻
P1U17-A04,error,这是我第一欠来中国。,这是我第一次来中国。,,欠 is missing the two ice dots
P1U17-A05,error,我买了一条库子。,我买了一条裤子。,,库 is only the sound part
P1U17-A06,error,我快定学中文。,我决定学中文。,,快 has 忄; decide has 冫
P1U17-A07,dialogue,今天天气怎么样？,很冷，多穿点儿衣服。,"很冷，多穿点儿衣服。 / 祝你幸福。 / 我买了袜子。 / 这是第一次。",
P1U17-A08,dialogue,你是第一次来中国吗？,是，这是我第一次来。,"是，这是我第一次来。 / 我腿疼。 / 很凉快。 / 他被批评了。",
P1U17-A09,dialogue,这是送给你的礼物。,谢谢你！,谢谢你！ / 我决定了。 / 脚很冷。 / 冬天来了。,
P1U17-A10,dialogue,你怎么了？,我走了一天，脚很疼。,"我走了一天，脚很疼。 / 祝你生日快乐。 / 我想喝冰水。 / 衬衫很漂亮。",
```

```text
冬天到了，北京很冷，外面的湖都结冰了。这是我第一次在北方过冬天。我去商店买了厚衬衫、厚裤子和袜子。晚上睡觉的时候，我盖两床被子。朋友说：“你最怕冷了！”我说：“对，可是我最喜欢冬天的雪。”
```

```csv
id,question,answer,options
P1U17-R01,外面的湖怎么了？,结冰了,结冰了 / 很凉快 / 很热 / 没有水
P1U17-R02,这是“我”第几次在北方过冬天？,第一次,第一次 / 第二次 / 第三次 / 每年
P1U17-R03,“我”买了什么？,衬衫、裤子和袜子,衬衫、裤子和袜子 / 被子 / 礼物 / 冰水
P1U17-R04,“我”最喜欢冬天的什么？,雪,雪 / 冷 / 冰 / 被子
```

## HSK1-U01 Greetings and identity

```csv
zh,py,en,radical,component,words,lookalikes
你,nǐ,you,亻,尔,"你们/nǐmen/you (plural)",您 他 称
我,wǒ,I; me,戈,—,"我们/wǒmen/we",找 饿 戒
他,tā,he,亻,也,"他们/tāmen/they",她 地 池
她,tā,she,女,也,"她们/tāmen/they (female)",他 地
们,men,(plural),亻,门,"我们/wǒmen/we; 你们/nǐmen/you all",门 问
好,hǎo,good,女,子,"你好/nǐ hǎo/hello; 好吃/hǎochī/tasty",妈 字
是,shì,to be,日,—,"不是/bú shì/is not; 是的/shì de/yes",星 提
不,bù,not,一,—,"不客气/bú kèqi/you're welcome; 不是/bú shì/is not",木 下 还
人,rén,person,人,—,"中国人/Zhōngguó rén/Chinese person; 大人/dàren/adult",入 八 个
叫,jiào,be called,口,丩,"叫做/jiàozuò/be called",收 叶
名字,míngzi,name,口,—,"你叫什么名字/nǐ jiào shénme míngzi/what's your name?",各 学
什么,shénme,what,亻,—,"为什么/wèi shénme/why",计 公
谢谢,xièxie,thank you,讠,—,"感谢/gǎnxiè/be grateful",树 射
不客气,bú kèqi,you're welcome,宀,—,"客人/kèrén/guest",各 气
对不起,duìbuqǐ,sorry,又,—,"对/duì/correct",时 赶
没关系,méi guānxi,it's OK,氵,—,"关系/guānxi/relationship",设 送
再见,zàijiàn,goodbye,冂,—,"再来/zài lái/come again; 见面/jiànmiàn/meet",贝 现
中国,Zhōngguó,China,丨,—,"中文/Zhōngwén/Chinese language; 国家/guójiā/country",图 园
老师,lǎoshī,teacher,老,—,"王老师/Wáng lǎoshī/Teacher Wang",考 帅
学生,xuésheng,student,子,—,"大学生/dàxuéshēng/university student",字 觉
```

```csv
id,tokens,en,targets
HSK1U01-S01,你好 ！ 你 叫 什么 名字 ？,Hi! What's your name?,你 好 叫 什么 名字
HSK1U01-S02,我 叫 王明 。 你 呢 ？,I'm Wang Ming. And you?,我 叫
HSK1U01-S03,你 是 老师 吗 ？,Are you a teacher?,你 是 老师
HSK1U01-S04,不 是 ， 我 是 学生 。,"No, I'm a student.",不 是 学生
HSK1U01-S05,你 是 中国人 吗 ？,Are you Chinese?,中国 人
HSK1U01-S06,她 不是 老师 。,She isn't a teacher.,她 老师
HSK1U01-S07,他们 是 中国人 吗 ？,Are they Chinese?,他 们 中国
HSK1U01-S08,他 叫 什么 名字 ？,What's his name?,他 叫 什么 名字
HSK1U01-S09,对不起 ！ 没关系 。,"""Sorry!"" ""It's OK.""",对不起 没关系
HSK1U01-S10,谢谢 你 ！ 不客气 。,"""Thank you!"" ""You're welcome.""",谢谢 不客气
HSK1U01-S11,我们 都 是 学生 。,We're all students.,我 们 学生
HSK1U01-S12,王 老师 是 中国人 。,Teacher Wang is Chinese.,老师 中国
HSK1U01-S13,你们 好 ！,Hello everyone!,你 们 好
HSK1U01-S14,我 不 是 中国人 。,I'm not Chinese.,不 是 中国
HSK1U01-S15,再见 ！ 明天 见 。,Goodbye! See you tomorrow.,再见
HSK1U01-S16,她 叫 李月 ， 是 我的 老师 。,"Her name is Li Yue, she's my teacher.",她 叫 老师
HSK1U01-S17,我的 名字 叫 大卫 。,My name is David.,名字 叫
HSK1U01-S18,你 是 学生 吗 ？ 是 。,"""Are you a student?"" ""Yes.""",学生 是
HSK1U01-S19,你们 是不是 中国人 ？,Are you Chinese or not?,你 们 中国
HSK1U01-S20,谢谢 老师 ！ 老师 再见 ！,"Thank you, teacher! Goodbye, teacher!",谢谢 老师 再见
```

```csv
id,type,prompt,answer,options,note
HSK1U01-A01,error,你叫什么名字吗？,你叫什么名字？,,No 吗 with a question word
HSK1U01-A02,error,我是好。,我很好。,,No 是 before an adjective
HSK1U01-A03,error,他不是中国。,他不是中国人。,,中国 is the country; a person needs 人
HSK1U01-A04,error,她是不老师。,她不是老师。,,不 goes before 是
HSK1U01-A05,error,我叫王明，你吗？,我叫王明，你呢？,,"""And you?"" is 呢"
HSK1U01-A06,error,他门是学生。,他们是学生。,,门 = door; plural 们 has 亻
HSK1U01-A07,dialogue,你叫什么名字？,我叫王明。,我叫王明。 / 我是中国。 / 不客气。 / 对不起。,
HSK1U01-A08,dialogue,谢谢！,不客气。,不客气。 / 没关系。 / 你好。 / 我是学生。,
HSK1U01-A09,dialogue,对不起！,没关系。,没关系。 / 不客气。 / 谢谢。 / 我叫李月。,
HSK1U01-A10,dialogue,你是老师吗？,不是，我是学生。,"不是，我是学生。 / 我叫大卫。 / 再见。 / 不客气。",
```

```text
你好！我叫大卫。我不是中国人，我是美国人。我是学生。我的老师叫王明，他是中国人。我的朋友叫李月，她也是学生。我们都是王老师的学生。
```

```csv
id,question,answer,options
HSK1U01-R01,大卫是中国人吗？,不是，他是美国人,不是，他是美国人 / 是 / 他是老师 / 不知道
HSK1U01-R02,大卫的老师叫什么名字？,王明,王明 / 李月 / 大卫 / 王大卫
HSK1U01-R03,李月是老师吗？,不是，她是学生,不是，她是学生 / 是 / 她是中国人 / 她叫王明
HSK1U01-R04,他们都是谁的学生？,王老师,王老师 / 李老师 / 大卫 / 李月
```

## HSK1-U02 Numbers and age

```csv
zh,py,en,radical,component,words,lookalikes
一,yī,one,一,—,"一个/yí ge/one; 第一/dì-yī/first",二 十
二,èr,two,二,—,"二十/èrshí/twenty; 第二/dì-èr/second",三 工
三,sān,three,一,—,"三个/sān ge/three; 三月/sānyuè/March",二 王
四,sì,four,囗,—,"四十/sìshí/forty",西 回
五,wǔ,five,二,—,"五月/wǔyuè/May; 五十/wǔshí/fifty",王 互
六,liù,six,八,—,"六个/liù ge/six",大 文
七,qī,seven,一,—,"七月/qīyuè/July",匕 也
八,bā,eight,八,—,"八十/bāshí/eighty",人 入 儿
九,jiǔ,nine,乙,—,"九月/jiǔyuè/September",几 丸 力
十,shí,ten,十,—,"十个/shí ge/ten",千 干 土
零,líng,zero,雨,令,"零下/língxià/below zero",冷 令 铃
百,bǎi,hundred,白,—,"一百/yìbǎi/one hundred",白 自 首
千,qiān,thousand,十,—,"一千/yìqiān/one thousand",干 午 十
两,liǎng,two (before measure words),一,—,"两个/liǎng ge/two",雨 丙 网
几,jǐ,how many (small numbers),几,—,"几个/jǐ ge/how many; 几岁/jǐ suì/how old (child)",九 儿 机
多少,duōshao,how many; how much,夕,—,"多少钱/duōshao qián/how much money",名 外
个,gè,(general measure word),人,—,"一个人/yí ge rén/one person",介 今
岁,suì,years old,山,—,"几岁/jǐ suì/how old; 岁数/suìshu/age",多 岩
大,dà,big; old (age),大,—,"多大/duō dà/how old; 大学/dàxué/university",太 天 犬
了,le,(change; completion),亅,—,"好了/hǎo le/done; 多大了/duō dà le/how old",子 予 丁
```

```csv
id,tokens,en,targets
HSK1U02-S01,你 多大 了 ？,How old are you?,大 了
HSK1U02-S02,我 二十八 岁 。,I'm twenty-eight.,二 十 八 岁
HSK1U02-S03,你们 有 几个 老师 ？,How many teachers do you have?,几 个
HSK1U02-S04,两个 老师 ， 九十个 学生 。,"Two teachers, and ninety students.",两 个 九 十
HSK1U02-S05,我 三十 岁 。,I'm thirty.,三 十 岁
HSK1U02-S06,你 弟弟 几岁 了 ？ 他 六岁 。,How old is your younger brother? He's six.,几 岁 了 六
HSK1U02-S07,三个 老师,three teachers,三 个
HSK1U02-S08,多少 学生 ？,How many students?,多少
HSK1U02-S09,一百 零八,one hundred and eight,一 百 零 八
HSK1U02-S10,我 有 两个 哥哥 。,I have two older brothers.,两 个
HSK1U02-S11,一年 有 十二个 月 。,A year has twelve months.,一 十 二 个
HSK1U02-S12,这儿 有 多少 人 ？,How many people are here?,多少
HSK1U02-S13,我 爷爷 九十 岁 了 。,My grandpa is ninety.,九 十 岁 了
HSK1U02-S14,我们 班 有 二十五个 学生 。,Our class has twenty-five students.,二 十 五 个
HSK1U02-S15,你 几岁 了 ？ 我 七岁 。,"""How old are you?"" ""I'm seven.""",几 岁 了 七
HSK1U02-S16,这个 城市 有 一千万 人 。,This city has ten million people.,一 千
HSK1U02-S17,她的 孩子 四岁 了 。,Her child is four now.,四 岁 了
HSK1U02-S18,一 加 一 等于 二 。,One plus one equals two.,一 二
HSK1U02-S19,我家 有 五个 人 。,There are five people in my family.,五 个
HSK1U02-S20,今天 零下 十 度 。,It's minus ten degrees today.,零 十
```

```csv
id,type,prompt,answer,options,note
HSK1U02-A01,error,我是二十五岁。,我二十五岁。,,No 是 with age
HSK1U02-A02,error,二个人,两个人,,Use 两 before a measure word
HSK1U02-A03,error,三学生,三个学生,,Number + measure word + noun
HSK1U02-A04,error,我有两哥哥。,我有两个哥哥。,,The measure word is missing
HSK1U02-A05,error,一百八 (meaning 108),一百零八,,一百八 means 180; 零 marks the empty tens place
HSK1U02-A06,error,我爸爸五十大。,我爸爸五十岁。,,Age takes 岁
HSK1U02-A07,dialogue,你多大了？,我二十五岁。,我二十五岁。 / 两个老师。 / 一百零八。 / 不客气。,
HSK1U02-A08,dialogue,你们有几个老师？,三个。,三个。 / 我三十岁。 / 九十九。 / 你好。,
HSK1U02-A09,dialogue,你弟弟几岁了？,他六岁。,他六岁。 / 他是学生。 / 六个。 / 六十。,
HSK1U02-A10,dialogue,你家有几个人？,五个人。,五个人。 / 五岁。 / 五百。 / 我是中国人。,
```

```text
我叫小明，今天是我的生日，我八岁了。我们班有三十个学生，两个老师。王老师四十岁，李老师二十九岁。今天老师和同学们都对我说：“生日快乐！”
```

```csv
id,question,answer,options
HSK1U02-R01,小明几岁了？,八岁,八岁 / 九岁 / 七岁 / 十八岁
HSK1U02-R02,他们班有多少个学生？,三十个,三十个 / 十三个 / 二十个 / 两个
HSK1U02-R03,王老师多大？,四十岁,四十岁 / 二十九岁 / 三十岁 / 八岁
HSK1U02-R04,班里有几个老师？,两个,两个 / 三个 / 一个 / 四个
```

## HSK1-U03 Family

```csv
zh,py,en,radical,component,words,lookalikes
家,jiā,home; family,宀,豕,"我家/wǒ jiā/my home; 家人/jiārén/family members",宝 字
爸爸,bàba,dad,父,—,"爸妈/bàmā/mom and dad",把 吧 巴
妈妈,māma,mom,女,—,"妈妈的/māma de/mom's",吗 码
哥哥,gēge,older brother,口,—,"大哥/dàgē/eldest brother",可 歌
姐姐,jiějie,older sister,女,—,"小姐/xiǎojie/miss",组 租
弟弟,dìdi,younger brother,弓,—,"兄弟/xiōngdì/brothers",第 递
妹妹,mèimei,younger sister,女,—,"姐妹/jiěmèi/sisters",味 末
儿子,érzi,son,儿,—,"女儿/nǚ'ér/daughter",几 字
女儿,nǚ'ér,daughter,女,—,"儿女/érnǚ/children",安 好
孩子,háizi,child,子,—,"小孩/xiǎohái/kid; 男孩/nánhái/boy",该 刻
朋友,péngyou,friend,月,—,"男朋友/nán péngyou/boyfriend; 好朋友/hǎo péngyou/good friend",明 有 反
有,yǒu,have; there is,月,—,"有名/yǒumíng/famous; 有意思/yǒu yìsi/interesting",右 友 布
没有,méiyǒu,not have,氵,—,"没有人/méiyǒu rén/nobody",设 投
的,de,(possessive),白,勺,"我的/wǒ de/my; 好的/hǎo de/OK",约 钓 白
和,hé,and,口,禾,"我和你/wǒ hé nǐ/you and me; 和平/hépíng/peace",知 利
也,yě,also,乙,—,"我也是/wǒ yě shì/me too",他 地 池
都,dōu,all; both,阝,者,"都是/dōu shì/all are",部 者 那
很,hěn,very,彳,艮,"很好/hěn hǎo/very good",银 跟 狠
爱,ài,love,爫,—,"爱人/àiren/spouse; 可爱/kě'ài/cute",受 爬
口,kǒu,(measure word for family members),口,—,"几口人/jǐ kǒu rén/how many in the family; 门口/ménkǒu/doorway",日 回
```

```csv
id,tokens,en,targets
HSK1U03-S01,你 家 有 几 口 人 ？,How many people are in your family?,家 有 口
HSK1U03-S02,我 家 有 四 口 人 ： 爸爸 、 妈妈 、 哥哥 和 我 。,"Four: Dad, Mom, my older brother and me.",家 爸爸 妈妈 哥哥 和
HSK1U03-S03,我 没有 哥哥 ， 我 有 两个 妹妹 。,"I don't have an older brother, I have two younger sisters.",没有 哥哥 有 妹妹
HSK1U03-S04,你 妹妹 也 是 学生 吗 ？,Is your younger sister a student too?,妹妹 也
HSK1U03-S05,她们 都 是 学生 。,They're all students.,都
HSK1U03-S06,我 没有 弟弟 。,I don't have a younger brother.,没有 弟弟
HSK1U03-S07,我 爸爸 和 妈妈 都 是 老师 。,My dad and mom are both teachers.,爸爸 和 妈妈 都
HSK1U03-S08,我 朋友 的 儿子 五 岁 。,My friend's son is five.,朋友 的 儿子
HSK1U03-S09,她 也 有 一个 女儿 。,She also has a daughter.,也 有 女儿
HSK1U03-S10,我 爱 我家 。,I love my family.,爱 家
HSK1U03-S11,我 姐姐 很 高 。,My older sister is very tall.,姐姐 很
HSK1U03-S12,这 是 我 的 朋友 。,This is my friend.,的 朋友
HSK1U03-S13,他们 的 孩子 很 可爱 。,Their child is very cute.,的 孩子 很 爱
HSK1U03-S14,你 有没有 男朋友 ？,Do you have a boyfriend?,有 没有 朋友
HSK1U03-S15,我 和 我 弟弟 都 喜欢 中国菜 。,My younger brother and I both like Chinese food.,和 弟弟 都
HSK1U03-S16,老师 的 女儿 也 是 老师 。,The teacher's daughter is also a teacher.,的 女儿 也
HSK1U03-S17,我 妈妈 很 爱 我 。,My mom loves me very much.,妈妈 很 爱
HSK1U03-S18,他 有 两个 儿子 。,He has two sons.,有 儿子
HSK1U03-S19,我们 都 是 好 朋友 。,We're all good friends.,都 朋友
HSK1U03-S20,我 哥哥 没有 孩子 。,My older brother has no children.,哥哥 没有 孩子
```

```csv
id,type,prompt,answer,options,note
HSK1U03-A01,error,我不有弟弟。,我没有弟弟。,,Never 不有
HSK1U03-A02,error,他是很好。,他很好。,,No 是 before an adjective
HSK1U03-A03,error,也我是学生。,我也是学生。,,也 goes right before the verb
HSK1U03-A04,error,他们是都老师。,他们都是老师。,,都 goes right before the verb
HSK1U03-A05,error,我有一哥哥。,我有一个哥哥。,,The measure word is missing
HSK1U03-A06,error,这是老师书。,这是老师的书。,,Possession needs 的 (except close people)
HSK1U03-A07,dialogue,你家有几口人？,四口人。,四口人。 / 四岁。 / 我爱我家。 / 我没有朋友。,
HSK1U03-A08,dialogue,你有哥哥吗？,没有，我有一个姐姐。,"没有，我有一个姐姐。 / 我不有哥哥。 / 他是很好。 / 我也是老师。",
HSK1U03-A09,dialogue,你爸爸妈妈是老师吗？,是，他们都是老师。,"是，他们都是老师。 / 我有妹妹。 / 我爱你。 / 她五岁。",
HSK1U03-A10,dialogue,我是学生。,我也是学生。,我也是学生。 / 我都是学生。 / 也我是学生。 / 我没有学生。,Tests 也 placement
```

```text
我叫李月，我家有五口人：爸爸、妈妈、哥哥、妹妹和我。我爸爸是医生，妈妈是老师。我哥哥二十五岁，他有一个女儿，三岁，很可爱。我妹妹十二岁，她也是学生。我很爱我的家。
```

```csv
id,question,answer,options
HSK1U03-R01,李月家有几口人？,五口,五口 / 四口 / 三口 / 六口
HSK1U03-R02,李月的妈妈是做什么的？,老师,老师 / 医生 / 学生 / 没有工作
HSK1U03-R03,哥哥的女儿几岁？,三岁,三岁 / 二十五岁 / 十二岁 / 五岁
HSK1U03-R04,谁也是学生？,妹妹,妹妹 / 哥哥 / 爸爸 / 妈妈
```

## HSK1-U04 Time and dates

```csv
zh,py,en,radical,component,words,lookalikes
今天,jīntiān,today,人,—,"今年/jīnnián/this year",令 会
明天,míngtiān,tomorrow,日,—,"明年/míngnián/next year",朋 名
昨天,zuótiān,yesterday,日,—,"昨晚/zuówǎn/last night",作 怎
年,nián,year,干,—,"今年/jīnnián/this year; 新年/xīnnián/New Year",午 牛
月,yuè,month; moon,月,—,"一月/yīyuè/January; 月亮/yuèliang/moon",日 用 目
日,rì,day (written dates),日,—,"生日/shēngrì/birthday; 日本/Rìběn/Japan",曰 目 白
号,hào,day of the month (spoken); number,口,—,"几号/jǐ hào/what date; 号码/hàomǎ/number",亏 写 叫
星期,xīngqī,week,日,—,"星期一/xīngqīyī/Monday; 星期天/xīngqītiān/Sunday",其 斯
天,tiān,day; sky,大,—,"每天/měitiān/every day; 天气/tiānqì/weather",夫 大 无
点,diǎn,o'clock; dot,灬,占,"三点/sān diǎn/three o'clock; 一点儿/yìdiǎnr/a little",占 店 站
分,fēn,minute,刀,—,"十分钟/shí fēnzhōng/ten minutes; 一分钱/yì fēn qián/one cent",公 今
半,bàn,half,十,—,"三点半/sān diǎn bàn/3:30; 一半/yíbàn/half",平 羊 伴
现在,xiànzài,now,王,—,"现在几点/xiànzài jǐ diǎn/what time is it",见 存
时候,shíhou,time; when,日,—,"什么时候/shénme shíhou/when; 小时候/xiǎoshíhou/childhood",对 侯
上午,shàngwǔ,morning (until noon),十,—,"今天上午/jīntiān shàngwǔ/this morning",牛 年 干
中午,zhōngwǔ,noon,丨,—,"中午饭/zhōngwǔfàn/lunch",牛 千
下午,xiàwǔ,afternoon,一,—,"下午好/xiàwǔ hǎo/good afternoon",上 不
早上,zǎoshang,early morning,日,—,"早上好/zǎoshang hǎo/good morning",草 旱
晚上,wǎnshang,evening,日,—,"晚上好/wǎnshang hǎo/good evening",免 换
生日,shēngrì,birthday,生,—,"生日快乐/shēngrì kuàilè/happy birthday",星 姓
```

```csv
id,tokens,en,targets
HSK1U04-S01,今天 几月 几号 ？,What's the date today?,今天 月 号
HSK1U04-S02,今天 十一月 二十五号 ， 星期三 。,"Today is November 25th, Wednesday.",今天 月 号 星期
HSK1U04-S03,明天 是 我的 生日 ！,Tomorrow is my birthday!,明天 生日
HSK1U04-S04,现在 几点 ？,What time is it now?,现在 点
HSK1U04-S05,现在 下午 两点 半 。,It's 2:30 in the afternoon.,现在 下午 点 半
HSK1U04-S06,昨天 是 星期天 。,Yesterday was Sunday.,昨天 星期
HSK1U04-S07,你的 生日 是 几月 几号 ？,When is your birthday?,生日 月 号
HSK1U04-S08,我的 生日 是 七月 九号 。,My birthday is July 9th.,生日 月 号
HSK1U04-S09,明天 星期五 。,Tomorrow is Friday.,明天 星期
HSK1U04-S10,我 早上 七点 起床 。,I get up at seven in the morning.,早上 点
HSK1U04-S11,我们 中午 十二点 吃饭 。,We eat at twelve noon.,中午 点
HSK1U04-S12,你 什么 时候 去 北京 ？,When are you going to Beijing?,时候
HSK1U04-S13,他 晚上 十点 睡觉 。,He goes to bed at ten in the evening.,晚上 点
HSK1U04-S14,上午 八点 半 上课 。,Class starts at 8:30 a.m.,上午 点 半
HSK1U04-S15,今年 是 二零二六 年 。,This year is 2026.,年
HSK1U04-S16,现在 是 三点 十五分 。,It's 3:15 now.,现在 点 分
HSK1U04-S17,一个 星期 有 七天 。,A week has seven days.,星期 天
HSK1U04-S18,我 昨天 晚上 没 睡觉 。,I didn't sleep last night.,昨天 晚上
HSK1U04-S19,今天 星期几 ？,What day of the week is it today?,今天 星期
HSK1U04-S20,我们 明天 下午 见 。,See you tomorrow afternoon.,明天 下午
```

```csv
id,type,prompt,answer,options,note
HSK1U04-A01,error,我去北京明天。,我明天去北京。,,Time words go before the verb
HSK1U04-A02,error,今天是不星期一。,今天不是星期一。,,不 goes before 是
HSK1U04-A03,error,二十五号十一月,十一月二十五号,,Dates go from big to small
HSK1U04-A04,error,现在三点半分。,现在三点半。,,半 replaces the minutes; no 分
HSK1U04-A05,error,下午八点 (meaning 8 a.m.),上午八点,,下午 = afternoon; use 上午 or 早上
HSK1U04-A06,error,星期七,星期天,,Sunday is 星期天 or 星期日
HSK1U04-A07,dialogue,今天星期几？,今天星期三。,今天星期三。 / 今天三号。 / 现在三点。 / 三月。,
HSK1U04-A08,dialogue,现在几点？,下午两点半。,下午两点半。 / 星期二。 / 七月九号。 / 明天。,
HSK1U04-A09,dialogue,你的生日是几月几号？,七月九号。,七月九号。 / 七点九分。 / 星期七。 / 九岁。,
HSK1U04-A10,dialogue,明天是我的生日！,是吗？生日快乐！,是吗？生日快乐！ / 我也是学生。 / 现在几点？ / 再见。,
```

```text
今天是十二月二十号，星期六。明天是我的生日。早上八点，我和妈妈去商店买东西。中午十二点，我们在饭店吃饭。下午三点半，我的朋友们来我家。晚上我们一起吃饭，很高兴。
```

```csv
id,question,answer,options
HSK1U04-R01,今天几月几号？,十二月二十号,十二月二十号 / 十二月二十一号 / 二十月十二号 / 十月二十号
HSK1U04-R02,“我”的生日是哪天？,明天,明天 / 今天 / 昨天 / 星期六
HSK1U04-R03,中午他们在哪儿吃饭？,饭店,饭店 / 家里 / 商店 / 学校
HSK1U04-R04,朋友们几点来？,下午三点半,下午三点半 / 早上八点 / 中午十二点 / 晚上
```

## HSK1-U05 Places

```csv
zh,py,en,radical,component,words,lookalikes
在,zài,be at; at,土,—,"在家/zài jiā/at home; 现在/xiànzài/now",存 再
这,zhè,this,辶,文,"这个/zhège/this one; 这儿/zhèr/here",还 过 送
那,nà,that,阝,—,"那个/nàge/that one; 那儿/nàr/there",哪 都 邦
哪,nǎ,which,口,那,"哪个/nǎge/which one; 哪儿/nǎr/where",那 啊
这儿,zhèr,here,辶,—,"在这儿/zài zhèr/here",那儿 哪儿
那儿,nàr,there,阝,—,"去那儿/qù nàr/go there",这儿 哪儿
哪儿,nǎr,where,口,—,"你去哪儿/nǐ qù nǎr/where are you going",这儿 那儿
里,lǐ,inside,里,—,"家里/jiāli/at home; 里面/lǐmiàn/inside",理 黑 星
上,shàng,on; above,一,—,"上面/shàngmiàn/on top; 上班/shàngbān/go to work",下 止
下,xià,under; below,一,—,"下面/xiàmiàn/below; 下课/xiàkè/class ends",上 不 卞
前面,qiánmiàn,in front,刂,—,"以前/yǐqián/before",剪 煎 后
后面,hòumiàn,behind,口,—,"以后/yǐhòu/after; 后来/hòulái/later",前 右 石
学校,xuéxiào,school,子,—,"大学/dàxué/university; 学习/xuéxí/study",字 交 较
医院,yīuyàn,hospital,匚,—,"医生/yīshēng/doctor",完 阮
商店,shāngdiàn,shop,广,—,"书店/shūdiàn/bookstore; 店员/diànyuán/shop assistant",点 占 站
饭店,fàndiàn,restaurant; hotel,饣,—,"饭馆/fànguǎn/restaurant",板 反
火车站,huǒchēzhàn,train station,立,—,"车站/chēzhàn/station; 火车/huǒchē/train",占 战 点
北京,Běijīng,Beijing,亠,—,"北方/běifāng/the north",比 景 凉
去,qù,go,土,—,"去年/qùnián/last year; 出去/chūqù/go out",云 丢 法
来,lái,come,木,—,"回来/huílái/come back; 来自/láizì/come from",米 末 未
```

```csv
id,tokens,en,targets
HSK1U05-S01,你 去 哪儿 ？,Where are you going?,去 哪儿
HSK1U05-S02,我 去 医院 。 你 呢 ？,I'm going to the hospital. And you?,去 医院
HSK1U05-S03,医院 在 哪儿 ？,Where is the hospital?,医院 在 哪儿
HSK1U05-S04,医院 在 学校 后面 。,The hospital is behind the school.,医院 在 学校 后面
HSK1U05-S05,那个 商店 也 在 那儿 吗 ？,Is that shop there too?,那 商店 在 那儿
HSK1U05-S06,商店 在 饭店 前面 。,The shop is in front of the restaurant.,商店 在 饭店 前面
HSK1U05-S07,老师 在 学校 里 。,The teacher is in the school.,在 学校 里
HSK1U05-S08,我 明天 去 北京 。,I'm going to Beijing tomorrow.,去 北京
HSK1U05-S09,这 是 商店 ， 那 是 饭店 。,"This is a shop, that is a restaurant.",这 商店 那 饭店
HSK1U05-S10,来 这儿 ！,Come here!,来 这儿
HSK1U05-S11,我 在 学校 学习 。,I study at school.,在 学校
HSK1U05-S12,书 在 桌子 上 。,The book is on the table.,在 上
HSK1U05-S13,他 不 在 家 。,He's not at home.,在
HSK1U05-S14,火车站 在 哪儿 ？,Where is the train station?,火车站 在 哪儿
HSK1U05-S15,你 哪 天 来 北京 ？,Which day are you coming to Beijing?,哪 来 北京
HSK1U05-S16,猫 在 桌子 下 。,The cat is under the table.,在 下
HSK1U05-S17,我家 前面 有 一个 商店 。,There's a shop in front of my home.,前面 商店
HSK1U05-S18,你 是 哪 国 人 ？,What country are you from?,哪
HSK1U05-S19,我 朋友 明天 来 我家 。,My friend is coming to my home tomorrow.,来
HSK1U05-S20,这个 饭店 很 好 ， 那个 不 好 。,"This restaurant is good, that one isn't.",这 饭店 那
```

```csv
id,type,prompt,answer,options,note
HSK1U05-A01,error,我学习在学校。,我在学校学习。,,The place comes before the action
HSK1U05-A02,error,我去到北京。,我去北京。,,去 + place with nothing between
HSK1U05-A03,error,书在桌子。,书在桌子上。,,Objects need a location word (上 / 里 / 下)
HSK1U05-A04,error,医院在哪儿吗？,医院在哪儿？,,No 吗 with a question word
HSK1U05-A05,error,我在北京里。,我在北京。,,Cities and countries don't take 里
HSK1U05-A06,error,这商店很好。,这个商店很好。,,这 / 那 + measure word + noun
HSK1U05-A07,dialogue,你去哪儿？,我去火车站。,我去火车站。 / 在学校后面。 / 这是商店。 / 我是北京人。,
HSK1U05-A08,dialogue,医院在哪儿？,在学校后面。,在学校后面。 / 我去医院。 / 医院很好。 / 来这儿！,
HSK1U05-A09,dialogue,王老师在吗？,不在，他在学校。,"不在，他在学校。 / 他是老师。 / 我去学校。 / 在桌子上。",
HSK1U05-A10,dialogue,你明天去哪儿？,我明天去北京。,我明天去北京。 / 我去北京明天。 / 我在北京去。 / 北京在那儿。,Tests time-word order
```

```text
我家在北京。我家前面有一个商店，后面有一个学校。学校旁边是医院。我妈妈是医生，她每天去医院。我爸爸在饭店工作。今天我朋友来我家，我们一起去火车站旁边的饭店吃饭。
```

```csv
id,question,answer,options
HSK1U05-R01,“我”家前面有什么？,商店,商店 / 学校 / 医院 / 饭店
HSK1U05-R02,学校旁边是什么？,医院,医院 / 商店 / 火车站 / 我家
HSK1U05-R03,妈妈每天去哪儿？,医院,医院 / 饭店 / 学校 / 商店
HSK1U05-R04,今天他们去哪儿吃饭？,火车站旁边的饭店,火车站旁边的饭店 / 家里 / 学校 / 医院
```
