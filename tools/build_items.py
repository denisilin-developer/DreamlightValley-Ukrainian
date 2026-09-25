# usage: build_items.py <batch dir> — after phase A: every short (≤6 words) English name from the root files
# (items, furniture, clothing, quests…) with its NEW Ukrainian → <batch dir>/items.tsv for phase B translators.
# When one English name got several translations, the most frequent wins and the rest are listed in items_conflicts.tsv.
import sys, json, glob, pathlib, collections

b = pathlib.Path(sys.argv[1])
rows = {}
for f in glob.glob(str(b / "A*.jsonl")):
    for r in map(json.loads, open(f, encoding="utf-8")):
        rows[r["id"]] = r
names = collections.defaultdict(collections.Counter)
for f in sorted(glob.glob(str(b / "out" / "A*.jsonl"))):
    for line in open(f, encoding="utf-8"):
        if line.strip():
            o = json.loads(line)
            en = rows[o["id"]]["en"]
            if len(en.split()) <= 6 and "\n" not in en and "<" not in en:
                names[en][o["uk"]] += 1
with open(b / "items.tsv", "w", encoding="utf-8") as fh, open(b / "items_conflicts.tsv", "w", encoding="utf-8") as fc:
    for en, c in sorted(names.items()):
        fh.write(f"{en}\t{c.most_common(1)[0][0]}\n")
        if len(c) > 1:
            fc.write(f"{en}\t" + " | ".join(f"{u} ×{n}" for u, n in c.most_common()) + "\n")
print(len(names), "names;", sum(len(c) > 1 for c in names.values()), "with conflicting translations")
