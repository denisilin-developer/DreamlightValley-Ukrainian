# usage: apply.py <merged dir> <out dir> <work dir>
# Copies merged → out, then writes every <work>/out_*.jsonl (sorted; later files override) translation into its .locbin file,
# re-reads each written file and asserts keys, order and untouched strings are unchanged.
import sys, json, glob, shutil, pathlib, collections
from locbin import read, write

src, dst, work = map(pathlib.Path, sys.argv[1:4])
shutil.copytree(src, dst)
rows = {}
for b in sorted(glob.glob(str(work / "batch_*.jsonl"))):
    for r in map(json.loads, open(b, encoding="utf-8")):
        rows[r["id"]] = r
by_file = collections.defaultdict(dict)
for o in sorted(glob.glob(str(work / "out_*.jsonl"))):
    for line in open(o, encoding="utf-8"):
        if line.strip():
            t = json.loads(line)
            r = rows[t["id"]]
            by_file[r["file"]][r["key"]] = t["uk"]
done = sum(len(v) for v in by_file.values())
for f, tr in by_file.items():
    before = read(src / f)
    d = dict(before)
    for k, v in tr.items():
        assert k in d, (f, k)
        d[k] = v
    write(dst / f, d)
    after = read(dst / f)
    assert list(after) == list(before)
    assert all(after[k] == (tr[k] if k in tr else before[k]) for k in after)
print(f"applied {done}/{len(rows)} translations into {len(by_file)} files")
