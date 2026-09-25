# usage: merge.py <new en-US dir> <ukr dir> <out dir> [<old en-US dir>]
# New English is the base (so new keys/files exist); Ukrainian overlays keys it has.
# With the old English (the version the Ukrainian was made from), keys whose English
# changed are sent back to translation too (the old Ukrainian stays in place meanwhile).
# Writes <out>.todo.tsv: file, key, english, reason (new|untranslated|reworded).
import sys, pathlib, re, csv
from locbin import read, write

CYR = re.compile("[А-Яа-яІіЇїЄєҐґ]")
SKIP = ("{placeholder}", "{donottranslate}")  # dev strings, case varies in the data
en_root, uk_root, out_root = map(pathlib.Path, sys.argv[1:4])
old_root = pathlib.Path(sys.argv[4]) if len(sys.argv) > 4 else None
stats = dict(files=0, new_files=0, strings=0, reused=0, todo=0, reworded=0, dropped_keys=0)


def needs_text(v):
    return not v.lower().startswith(SKIP) and re.search("[A-Za-z]{3,}", re.sub(r"<[^>]+>|\{[^}]+\}", "", v))


with open(out_root.with_suffix(".todo.tsv"), "w", newline="", encoding="utf-8") as fh:
    todo = csv.writer(fh, delimiter="\t")
    for en_p in sorted(en_root.rglob("*.locbin")):
        rel = en_p.relative_to(en_root)
        uk_p = uk_root / rel
        en = read(en_p)
        uk = read(uk_p) if uk_p.exists() else {}
        old = read(old_root / rel) if old_root and (old_root / rel).exists() else {}
        stats["files"] += 1
        stats["new_files"] += not uk_p.exists()
        stats["dropped_keys"] += len(uk.keys() - en.keys())
        out = {}
        for k, v in en.items():
            stats["strings"] += 1
            translated = k in uk and CYR.search(uk[k])
            out[k] = uk[k] if translated else uk.get(k, v)
            if translated and old_root and k in old and old[k] != v and needs_text(v):
                todo.writerow([str(rel), k, v, "reworded"])
                stats["reworded"] += 1
            elif translated:
                stats["reused"] += 1
            elif needs_text(v) and rel.name != "legal.locbin":
                todo.writerow([str(rel), k, v, "new" if k not in uk else "untranslated"])
                stats["todo"] += 1
        (out_root / rel).parent.mkdir(parents=True, exist_ok=True)
        write(out_root / rel, out)
print(stats)
