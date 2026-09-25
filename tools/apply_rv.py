# usage: apply_rv.py <current uk dir> <out dir> <batch dir>
# Copies current → out and writes every <batch dir>/out/*.jsonl line (sorted; later files override, so
# zz_*.jsonl fix files win) into its .locbin. Re-reads each file and asserts key order + untouched strings.
import sys, json, glob, shutil, pathlib, collections
from locbin import read, write

src, dst, b = map(pathlib.Path, sys.argv[1:4])
shutil.copytree(src, dst)
rows = {}
for f in glob.glob(str(b / "[AB]*.jsonl")):
    for r in map(json.loads, open(f, encoding="utf-8")):
        rows[r["id"]] = (r["file"], r["key"])
by_file = collections.defaultdict(dict)
for f in sorted(glob.glob(str(b / "out" / "*.jsonl"))):
    for line in open(f, encoding="utf-8"):
        if line.strip():
            o = json.loads(line)
            fl, k = rows[o["id"]]
            by_file[fl][k] = o["uk"]
for fl, tr in by_file.items():
    before = read(src / fl)
    d = dict(before)
    for k, v in tr.items():
        assert k in d, (fl, k)
        d[k] = v
    write(dst / fl, d)
    after = read(dst / fl)
    assert list(after) == list(before)
    assert all(after[k] == tr.get(k, before[k]) for k in after)
done = sum(len(v) for v in by_file.values())
print(f"applied {done}/{len(rows)} rows into {len(by_file)} files")
