# usage: python3 check.py NN  — validates out_NN.jsonl against batch_NN.jsonl
import sys, json, re, collections

TOK = re.compile(r"<[^>]*>|\{\{?[^{}]*\}\}?|\\n|\n")
CYR = re.compile("[А-Яа-яІіЇїЄєҐґ]")
nn = sys.argv[1]
batch = {r["id"]: r for r in map(json.loads, open(f"batch_{nn}.jsonl", encoding="utf-8"))}
problems = []
out = {}
kept = set()
try:
    lines = open(f"out_{nn}.jsonl", encoding="utf-8").read().splitlines()
except FileNotFoundError:
    sys.exit(f"out_{nn}.jsonl missing")
for n, line in enumerate(lines, 1):
    if not line.strip():
        continue
    try:
        o = json.loads(line)
        out[o["id"]] = o["uk"]
        if o.get("keep"): kept.add(o["id"])
    except Exception as e:
        problems.append(f"line {n}: bad JSON ({e})")
for i, r in batch.items():
    if i not in out:
        problems.append(f"id {i}: missing")
        continue
    uk = out[i]
    if collections.Counter(TOK.findall(uk)) != collections.Counter(TOK.findall(r["en"])):
        problems.append(f"id {i}: markup/linebreak mismatch  en={TOK.findall(r['en'])}  uk={TOK.findall(uk)}")
    if i not in kept and not CYR.search(uk) and re.search("[A-Za-z]{3,}", TOK.sub("", r["en"])):
        problems.append(f"id {i}: no Cyrillic (untranslated?)  {uk[:80]!r}")
    if uk.strip() != uk and r["en"].strip() == r["en"]:
        problems.append(f"id {i}: stray leading/trailing whitespace")
extra = out.keys() - batch.keys()
if extra:
    problems.append(f"unknown ids: {sorted(extra)[:10]}")
print("\n".join(problems[:60]) if problems else f"OK {len(out)}/{len(batch)}")
if len(problems) > 60:
    print(f"... {len(problems) - 60} more")
