# usage: audit.py <work dir>
# Cross-batch checks that check.py (per batch) cannot see:
#  - every id translated exactly once (later out_* files override earlier ones)
#  - numbers match (catches a translation landing on the wrong id)
#  - identical short English strings translated differently (item/place names must match)
import sys, json, glob, re, collections, pathlib

work = pathlib.Path(sys.argv[1])
rows = {}
for b in sorted(glob.glob(str(work / "batch_*.jsonl"))):
    for r in map(json.loads, open(b, encoding="utf-8")):
        rows[r["id"]] = r
out = {}
for o in sorted(glob.glob(str(work / "out_*.jsonl"))):
    for line in open(o, encoding="utf-8"):
        if line.strip():
            t = json.loads(line)
            out[t["id"]] = t["uk"]
print(f"rows {len(rows)}, translated {len(out)}, missing {sorted(rows.keys() - out.keys())[:20]}")

# drop thousands separators first: 1,000 (en) and 1 000 / 1000 (uk) are the same number
nums = lambda s: sorted(re.findall(r"\d+", re.sub(r"(?<=\d)[ ,\u00a0\u202f](?=\d{3}\b)", "", re.sub(r"<[^>]+>|\{[^}]+\}", "", s))))
print("\n== numbers differ (check alignment; 1,000 → 1000 is fine)")
for i in sorted(rows.keys() & out.keys()):
    if nums(rows[i]["en"]) != nums(out[i]):
        print(f"{i}: {rows[i]['en'][:90]!r} => {out[i][:90]!r}")

print("\n== same short English, different Ukrainian (unify names; dialogue may vary)")
variants = collections.defaultdict(collections.Counter)
for i in rows.keys() & out.keys():
    if len(rows[i]["en"].split()) <= 5:
        variants[rows[i]["en"]][out[i]] += 1
for en, c in sorted(variants.items()):
    if len(c) > 1:
        print(f"{en!r}: {dict(c)}")
