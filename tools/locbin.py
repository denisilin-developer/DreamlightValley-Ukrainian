# locbin = protobuf: repeated field 1 { 1: key (str), 2: value (str) }
import sys, pathlib, re, collections

def varint(b, i):
    n = s = 0
    while True:
        c = b[i]; i += 1; n |= (c & 0x7f) << s; s += 7
        if c < 0x80: return n, i

def fields(b):
    i = 0
    while i < len(b):
        tag, i = varint(b, i)
        assert tag & 7 == 2, f"unexpected wire type {tag}"
        ln, i = varint(b, i)
        yield tag >> 3, b[i:i+ln]; i += ln

def read(path):
    out = {}
    for f, entry in fields(pathlib.Path(path).read_bytes()):
        assert f == 1, f"unexpected top field {f}"
        d = {k: v.decode() for k, v in fields(entry)}
        assert set(d) <= {1, 2}, f"unexpected entry fields {set(d)}"
        out[d[1]] = d.get(2, "")
    return out

if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1])
    total = ukr = eng = empty = 0; files = 0
    for p in root.rglob("*.locbin"):
        files += 1
        for k, v in read(p).items():
            total += 1
            if not v.strip(): empty += 1
            elif re.search("[А-Яа-яІіЇїЄєҐґ]", v): ukr += 1
            elif re.search("[A-Za-z]{3,}", re.sub(r"<[^>]+>|\{[^}]+\}", "", v)): eng += 1
    print(f"files={files} strings={total} ukrainian={ukr} latin-only={eng} empty={empty}")

def _v(n):
    o = b""
    while True:
        c = n & 0x7f; n >>= 7
        if not n: return o + bytes([c])
        o += bytes([c | 0x80])

def _f(num, b): return _v(num << 3 | 2) + _v(len(b)) + b

def write(path, d):
    pathlib.Path(path).write_bytes(b"".join(
        _f(1, _f(1, k.encode()) + _f(2, v.encode())) for k, v in d.items()))
