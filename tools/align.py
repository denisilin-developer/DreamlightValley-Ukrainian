# usage: python3 align.py B194 [B195 ...] — longest run of consecutive lines that look shifted ('?' or length mismatch)
import sys, json
for b in sys.argv[1:]:
    out={}
    for l in open(f"out/{b}.jsonl"):
        if l.strip(): o=json.loads(l); out[o["id"]]=o["uk"]
    run=best=0; at=None
    for r in map(json.loads, open(b+".jsonl")):
        uk=out.get(r["id"],""); en=r["en"]
        q=en.rstrip().endswith("?")!=uk.rstrip().endswith("?"); ratio=len(uk)/max(len(en),1)
        run=run+1 if ((q and len(en)>12) or (len(en)>40 and not 0.45<ratio<2.4)) else 0
        if run>best: best,at=run,r["id"]
    print(b, "OK" if best<3 else f"SUSPECT run={best} ending at id {at}")
