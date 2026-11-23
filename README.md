# 长大 · Grow Up in Chinese

Mobile PWA: Mandarin from 儿歌 to 高考 and the news. Four skills per word (read, write, listen, speak), each on its own FSRS schedule.

## Run locally
    node serve.cjs          # http://localhost:8642
Tests: `node tools/test-core.cjs` (logic) and `node tools/validate.cjs` (content linter, run after adding a unit).

## Put it on your phone
Microphone and speech recognition need HTTPS. Push this folder to a GitHub repo, enable GitHub Pages, open the URL on the phone, then:
- iPhone (Safari): Share → Add to Home Screen.
- Android (Chrome): ⋮ → Install app.

## Adding a unit
Drop `data/sXuYY.json` (schema in ARCHITECTURE.md), add its filename to `data/index.json`, run `node tools/validate.cjs`.

## Browser limits and workarounds
- iOS speech recognition: Safari exposes webkitSpeechRecognition through Siri dictation; it needs Siri & Dictation on with Chinese (Mainland) added, and it is flaky inside home-screen apps. When it fails or is missing the app records you (MediaRecorder), plays your voice next to the native audio and lets you grade yourself. Settings → Speech recognition → off forces this mode.
- Firefox has no speech recognition at all: same self-grade fallback.
- Voices: iPhone → Settings → Accessibility → Spoken Content → Voices → Chinese (China mainland), download an Enhanced voice. Android → Google Speech Services Chinese voice data. Pick it in the app's settings.
- Tone analysis compares your pitch with tone templates (Chao 55/35/214/51), since browsers cannot capture TTS audio to compare against. Syllables are split by voiced runs, so speak clearly; fast connected speech can mis-split.
- Handwriting stroke data loads per character from jsDelivr and is cached for offline use.
- iOS may clear site storage of non-installed sites after weeks unused. Install to the home screen and use Export regularly.

## Credits
- Native recordings: [audio-cmn](https://github.com/hugolpz/audio-cmn) by Hugo Lopez (INALCO). Tone syllables voiced by Chen Wang, HSK words by Yue Tan (shtooka.net). CC BY-SA. Streamed from jsDelivr, pinned to commit f759a0f; `data/audio.json` lists which recordings exist.
- Hanzi → pinyin for speech grading: [pinyin-pro](https://github.com/zh-lx/pinyin-pro) (MIT).
- Stroke data: [Hanzi Writer](https://hanziwriter.org) and Make Me a Hanzi.
