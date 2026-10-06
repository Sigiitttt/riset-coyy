import json
import difflib
from pathlib import Path

f1 = Path(r"kode/4-4-irisan-ringkas-optimasi-8p2w-selesai.ipynb")
f2 = Path(r"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb")

nb1 = json.load(open(f1, encoding="utf-8"))
nb2 = json.load(open(f2, encoding="utf-8"))

print(f"Cells: f1={len(nb1['cells'])}, f2={len(nb2['cells'])}")

diffs = []
for i in range(max(len(nb1['cells']), len(nb2['cells']))):
    c1 = nb1['cells'][i] if i < len(nb1['cells']) else None
    c2 = nb2['cells'][i] if i < len(nb2['cells']) else None
    if c1 is None or c2 is None:
        diffs.append((i, "EXTRA CELL"))
        continue
    s1 = "".join(c1.get("source", []))
    s2 = "".join(c2.get("source", []))
    if s1.strip() != s2.strip():
        diffs.append((i, "DIFF"))

print(f"Total diff cells: {len(diffs)}")
for idx, r in diffs:
    print(f"\n=== Cell {idx} ===")
    s1 = "".join(nb1['cells'][idx].get("source", [])).splitlines()
    s2 = "".join(nb2['cells'][idx].get("source", [])).splitlines() if idx < len(nb2['cells']) else []
    for line in difflib.unified_diff(s1, s2, fromfile="8p2w-kemarin", tofile="sk1-folder-4.4", lineterm=""):
        print(line)
