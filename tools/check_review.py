# usage: python3 check.py <BATCH>   e.g. check.py B017 — validates out/<BATCH>.jsonl against <BATCH>.jsonl
import sys, json, re, collections

TOK = re.compile(r"<[^>]*>|\{\{?[^{}]*\}\}?|\\n|\n")
CYR = re.compile("[А-Яа-яІіЇїЄєҐґ]")
RUONLY = re.compile("[ЁёЫыЭэЪъ]")
BRANDS = re.compile(r"Disney|Pixar|Gameloft|PlayStation|PS\d|Xbox|Nintendo|Switch|Steam|Epic|Apple|Discord|DreamSnaps|"
                    r"DreamTeams|PlayFab|Lucasfilm|Marvel|Google|Android|iOS|Windows|Mac|TikTok|YouTube|Instagram|"
                    r"Facebook|Twitter|Twitch|Reddit|http\S*|www\S*|\S+\.com\S*|DDV|ID|FAQ|UI|HUD|FPS|HDR|VSync|DLC|QWERTY|AZERTY")
VY = re.compile(r"\b(ви|вам|вас|вами|ваш|ваша|ваше|ваші|вашого|вашої|вашому|вашим|вашій|ваших)\b|"
                r"(?:^|[.!?:;—«(]\s*)(?!навіть\b|звідти\b|хоч\b)\w+(іть|іться|айте|айтеся|уйте|ийте|ьте)\b", re.I)  # imperative opens a clause
M1 = re.compile(r"\bя\s+(?:(?:не|вже|так|ж|би|б|ще|теж|також|лише|просто|навіть|аж)\s+)*\w{2,}(?:[^л\W]в|вся)\b|"
                r"\bя\s+(?:такий\s+|дуже\s+)?(?:радий|впевнений|певен|готовий|повинен|вдячний|щасливий|згоден|сам)\b", re.I)
F1 = re.compile(r"\bя\s+(?:(?:не|вже|так|ж|би|б|ще|теж|також|лише|просто|навіть|аж)\s+)*\w{2,}(?:ла|лася)\b|"
                r"\bя\s+(?:така\s+|дуже\s+)?(?:рада|впевнена|певна|готова|повинна|вдячна|щаслива|згодна|сама)\b", re.I)

b = sys.argv[1]
batch = {r["id"]: r for r in map(json.loads, open(f"{b}.jsonl", encoding="utf-8"))}
out, kept, errs, warns = {}, set(), [], []
try:
    lines = open(f"out/{b}.jsonl", encoding="utf-8").read().splitlines()
except FileNotFoundError:
    sys.exit(f"out/{b}.jsonl missing")
for n, line in enumerate(lines, 1):
    if not line.strip():
        continue
    try:
        o = json.loads(line)
        out[o["id"]] = o["uk"]
        if o.get("keep"):
            kept.add(o["id"])
    except Exception as e:
        errs.append(f"line {n}: bad JSON ({e})")
for i, r in batch.items():
    if i not in out:
        errs.append(f"id {i}: missing")
        continue
    uk, en = out[i], r["en"]
    if collections.Counter(TOK.findall(uk)) != collections.Counter(TOK.findall(en)):
        errs.append(f"id {i}: markup/linebreak mismatch en={TOK.findall(en)} uk={TOK.findall(uk)}")
    if uk.strip() != uk and en.strip() == en:
        errs.append(f"id {i}: stray leading/trailing whitespace")
    if i in kept:
        continue
    text = TOK.sub(" ", uk)
    if not CYR.search(text) and re.search("[A-Za-z]{3,}", TOK.sub("", en)):
        errs.append(f"id {i}: no Ukrainian text (untranslated? add keep:true if intentional) {uk[:70]!r}")
    if RUONLY.search(text):
        errs.append(f"id {i}: Russian letters (ё/ы/э/ъ) {uk[:70]!r}")
    latin = [w for w in re.findall(r"[A-Za-z][A-Za-z'’\-]{2,}", BRANDS.sub(" ", text))]
    if latin:
        errs.append(f"id {i}: English words left {latin[:4]} (translate, or keep:true if a brand)")
    if re.search(r"\bГей\b", uk) and re.search(r"\bHey\b", en):
        errs.append(f"id {i}: 'Hey' → «Гей» — use Привіт/Агов/Слухай")
    if VY.search(text) and not re.search(r"\b(you all|you guys|everyone|y'all|you two|both of you)\b", en, re.I):
        warns.append(f"id {i}: «ви»/-іть form — player is «ти» (ignore if several people are addressed) {uk[:70]!r}")
    g = r.get("speaker_gender")
    if g == "f" and M1.search(text) and not F1.search(text):
        warns.append(f"id {i}: speaker is female but first person looks masculine {uk[:70]!r}")
    if g == "m" and F1.search(text) and not M1.search(text):
        warns.append(f"id {i}: speaker is male but first person looks feminine {uk[:70]!r}")
extra = out.keys() - batch.keys()
if extra:
    errs.append(f"unknown ids: {sorted(extra)[:10]}")
for m in errs[:50]:
    print("ERROR", m)
for m in warns[:40]:
    print("WARN ", m)
if len(errs) > 50 or len(warns) > 40:
    print(f"... {max(0, len(errs) - 50)} more errors, {max(0, len(warns) - 40)} more warnings")
if not errs:
    print(f"OK {len(out)}/{len(batch)}" + (f" ({len(warns)} warnings reviewed?)" if warns else ""))
