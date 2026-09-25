# usage: make_batches.py <new en dir> <final uk dir> <ru dir> <out dir> <words per batch>
# Every translatable string → one row with en / ru / current uk / speaker, split into
# phase A (root .locbin: items, UI, quests) and phase B (dialogue folders).
import sys, pathlib, re, json
from locbin import read

en_root, uk_root, ru_root, out = map(pathlib.Path, sys.argv[1:5])
per = int(sys.argv[5])
out.mkdir(parents=True, exist_ok=True)
RU = re.compile("[А-Яа-яЁё]")
gender = json.load(open(out / "speaker_gender_auto.json"))


def translatable(v):
    return (not v.lower().startswith(("{placeholder}", "{donottranslate}"))
            and re.search("[A-Za-z]{2,}", re.sub(r"<[^>]+>|\{[^}]+\}", "", v)))


rows = {"A": [], "B": []}
rid = 0
for p in sorted(en_root.rglob("*.locbin")):
    rel = p.relative_to(en_root)
    if rel.name == "legal.locbin":
        continue
    en = read(p)
    uk = read(uk_root / rel)
    rp = ru_root / rel
    ru = read(rp) if rp.exists() else {}
    phase = "B" if len(rel.parts) > 1 else "A"
    for k, v in en.items():
        if not translatable(v):
            continue
        r = {"id": rid, "file": str(rel), "key": k, "en": v, "uk": uk.get(k, v)}
        if RU.search(ru.get(k, "")):
            r["ru"] = ru[k]
        if phase == "B":
            sp = re.match(r"([^_!]+)", k).group(1)
            r["speaker"] = sp
            if gender.get(sp) in ("m", "f"):
                r["speaker_gender"] = gender[sp]
        rows[phase].append(r)
        rid += 1

n = 0
for phase in "AB":
    batch, words, prev = [], 0, None
    for r in rows[phase]:
        folder = r["file"].split("/")[0]
        if batch and ((words >= per and folder != prev) or words >= per * 1.4):
            with open(out / f"{phase}{n:03d}.jsonl", "w", encoding="utf-8") as fh:
                fh.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in batch)
            n += 1
            batch, words = [], 0
        batch.append(r)
        words += len(r["en"].split())
        prev = folder
    with open(out / f"{phase}{n:03d}.jsonl", "w", encoding="utf-8") as fh:
        fh.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in batch)
    n += 1
    print(phase, len(rows[phase]), "rows", sum(len(r["en"].split()) for r in rows[phase]), "words")
print("batches", n)
