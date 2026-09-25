# usage: prepare.py <new en-US dir> <merged dir> <todo.tsv> <work dir> [batches=11]
# Builds the translation memory from strings already in Ukrainian, splits the todo list
# into batches of roughly equal word count (cut at dialogue-folder boundaries so a
# conversation stays in one batch), and copies GUIDE.md + check.py into <work dir>.
import sys, pathlib, re, csv, json, shutil
from locbin import read

CYR = re.compile("[А-Яа-яІіЇїЄєҐґ]")
en_root, merged, todo_tsv, work = map(pathlib.Path, sys.argv[1:5])
n_batches = int(sys.argv[5]) if len(sys.argv) > 5 else 11
work.mkdir(parents=True, exist_ok=True)
here = pathlib.Path(__file__).parent

tm = {}
for p in sorted(en_root.rglob("*.locbin")):
    en, uk = read(p), read(merged / p.relative_to(en_root))
    for k, v in en.items():
        if v.strip() and CYR.search(uk.get(k, "")):
            tm.setdefault(v, uk[k])
esc = lambda s: s.replace("\t", " ").replace("\n", "\\n")
with open(work / "tm.tsv", "w", encoding="utf-8") as f:
    f.writelines(f"{esc(e)}\t{esc(u)}\n" for e, u in tm.items())
with open(work / "glossary_short.tsv", "w", encoding="utf-8") as f:
    f.writelines(f"{esc(e)}\t{esc(u)}\n" for e, u in sorted(tm.items()) if len(e.split()) <= 4)

rows, cache = [], {}
for i, (f, k, en, *_reason) in enumerate(csv.reader(open(todo_tsv, encoding="utf-8"), delimiter="\t")):
    r = {"id": i, "file": f, "key": k, "en": en}
    if k.endswith("_m"):
        r["pair"] = "m"
    elif k.endswith("_f"):
        d = cache.setdefault(f, read(en_root / f))
        if k[:-2] + "_m" in d:
            r["pair"] = "f"
    rows.append(r)

target = sum(len(r["en"].split()) for r in rows) / n_batches
batches, words = [[]], 0
for j, r in enumerate(rows):
    folder = r["file"].split("/")[0]
    prev = rows[j - 1]["file"].split("/")[0] if j else folder
    if batches[-1] and ((words >= target and folder != prev) or words >= target * 1.3) and len(batches) < n_batches:
        batches.append([])
        words = 0
    batches[-1].append(r)
    words += len(r["en"].split())
for n, b in enumerate(batches):
    with open(work / f"batch_{n:02d}.jsonl", "w", encoding="utf-8") as fh:
        fh.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in b)
    print(f"batch_{n:02d}: {len(b)} rows, {sum(len(r['en'].split()) for r in b)} words, "
          f"{b[0]['file'].split('/')[0]} → {b[-1]['file'].split('/')[0]}")
shutil.copy(here / "check.py", work)
shutil.copy(here.parent / "references" / "GUIDE.md", work)
print(f"tm pairs {len(tm)}, rows {len(rows)}, gendered {sum('pair' in r for r in rows)}")
