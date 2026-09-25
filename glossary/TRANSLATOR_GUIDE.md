# Disney Dreamlight Valley → Ukrainian: full re-translation guide

The current Ukrainian (`uk` field) is mostly raw MACHINE translation: literal, clumsy, wrong genders, English words left
inside, broken grammar, lost jokes. You are rewriting it into natural, fluent, fun Ukrainian that a native speaker
would enjoy reading — as if Disney had localized the game officially. Not Russian, no russisms, no surzhyk.

## What each row gives you
- `en` — the SOURCE. Translate the meaning, tone and intent of the English.
- `ru` — a good human Russian fan localization (when present). Use it as a hint: who is speaking and their gender,
  how a joke/pun/rhyme was adapted, how an idiom was rendered. Do NOT copy Russian word order or calques
  (e.g. «являтися», «приймати участь», «на протязі», «згідно з», «вибачаюсь», «слідуючий» are wrong in Ukrainian).
- `uk` — the current Ukrainian. Keep it if it is already good (many short strings are fine); otherwise rewrite.
- `speaker` / `speaker_gender` (dialogue) — who says the line. `Player` = the player's own reply.
  WARNING: the tag is derived from the key and is often the conversation OWNER, not the speaker — player replies
  are frequently tagged with the villager's name. Decide the real speaker from the scene and the Russian line
  (Russian verb endings show the gender); player replies are always masculine.

## Grammar
- **Speaker gender**: a female speaker uses feminine first-person forms (я рада, я знала, я сама). If
  `speaker_gender` is missing, infer it from the Russian line (сказала/сказал) or the character.
  `Player` speaks in MASCULINE forms, and others address the player in masculine (ти зробив, ти прийшов).
- **Address**: the player is ALWAYS «ти» — in dialogue, quest steps, hints and UI too:
  «Поговори з Мерліном», «Збери 10 яблук», «Тобі підказали…». Use «ви» only when the English clearly addresses
  several people, or a character is formally addressing a stranger/elder (e.g. to Скрудж as «містере Макдак»).
- Villagers call each other and the player by name in the vocative where natural (Мерліне, Міккі, Вуді).

## Style
- Keep each character's voice: Scrooge is stingy and Scottish-flavoured (еге ж, трясця, мої грошенята), Merlin is a
  wise, slightly scatterbrained wizard, Goofy says «Ґа-гік!»-style interjections, Olaf is naïve and sunny, Gaston
  boastful, Ursula sly and theatrical, Remy passionate about food, WALL-E beeps, Stitch speaks broken language.
- **Localize jokes, puns and wordplay** instead of translating words: invent an equivalent Ukrainian pun, rhyme or
  alliteration (see how the Russian did it). Rhymed lines stay rhymed. Deliberate misspellings/accents stay playful.
- Interjections: "Hey" → «Гей» is WRONG (it is a Ukrainian exclamation only in songs) — use «Привіт», «Агов», «Слухай»,
  «Ей» depending on context. "Oh" → «О», «Ох», «Ой». "Wow" → «Ого», «Ух ти».
- Idioms: translate the meaning, not the words ("break a leg" → «ні пуху ні пера» is fine; «хай тобі щастить» better).
- Keep it concise — UI labels and item names must fit on screen; do not make strings much longer than the English.
- Item/place names are Proper Nouns in Title-ish case like the English ("Antique Camera" → «Старовинна камера»);
  inside quest text they appear in <ActivityItem> tags and must match the item's own name (decline naturally).

## Names
- `glossary.tsv` (columns english, ukrainian, gender, note) is FIXED — always use those forms (declined naturally).
  Look up every proper noun: `grep -iF "wishblossom" glossary.tsv`.
- `glossary_additions.tsv` (same columns) has the same authority: event, quest, item-family and feature names
  unified after phase A (e.g. Trick-or-Treat, Sugar Rush, Memory Mania, Majestea). Grep BOTH files for every name.
  If glossary/additions and items.tsv disagree, the glossary files win.
- Read `glossary_notes.md` once — it explains the naming principles for anything not in the list.
- Phase B only: `items.tsv` holds the NEW Ukrainian names of every item/furniture/clothing/quest item (english⇥ukrainian).
  When a line mentions an item — especially inside <ActivityItem>…</ActivityItem> — use that name:
  `grep -F "Antique Camera" items.tsv`.
- Never leave English words in Ukrainian text, except real brand names: Disney, Pixar, Gameloft, PlayStation, Xbox,
  Nintendo, Steam, Epic Games, Apple, Discord, DreamSnaps, PlayFab, URLs, and the game title
  "Disney Dreamlight Valley" when used as the product name. Place names are localized per glossary.

## Hard rules (check.py enforces them)
- Every markup token must survive byte-identical and the same number of times: `{PlayerName}`, `{TargetNPC}`, `{0}`,
  `{{amount}/{total}}`, `{character:...}`, `<ActivityItem>…</ActivityItem>`, `<Lore>…</Lore>`, `<b>`, `<i>`, `<br>`,
  `<color=…>`, `<size=…>`, `<align=…>`, `<indent=…>`, `<sprite=…>`, `<smallcaps>` etc. Translate text INSIDE tags only.
- Same number of real line breaks (`\n` in JSON) and literal backslash-n (`\\n` in JSON).
- One output line per input id; no leading/trailing spaces unless the English has them.
- For lines that must stay non-Ukrainian (brand only, a URL, a language's own name, an onomatopoeia like "Beep!"),
  add `"keep": true`.

## Workflow
1. Read this guide, `glossary_notes.md`, and skim `glossary.tsv`.
2. Read your batch file in pieces (e.g. `sed -n '1,120p' B017.jsonl`). Dialogue rows are in conversation order —
   read them as a scene.
3. Append results to `out/<BATCH>.jsonl`, one JSON object per line: `{"id": 123, "uk": "…"}` — write every ~100 rows
   so nothing is lost. Name any helper script `tmp_<BATCH>.py` (other translators share this folder).
4. Run `python3 check.py <BATCH>` (e.g. `python3 check.py B017`). Fix all ERRORs; review the WARNings
   (fix unless the warning is wrong for that line). Re-run until it prints OK.
