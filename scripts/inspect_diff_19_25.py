import json
import difflib
from pathlib import Path

f1 = Path(r"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb")
f2 = Path(r"4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb")

nb1 = json.load(open(f1, encoding="utf-8"))
nb2 = json.load(open(f2, encoding="utf-8"))

for idx in [4, 19, 25]:
    s1 = "".join(nb1["cells"][idx]["source"]).splitlines()
    s2 = "".join(nb2["cells"][idx]["source"]).splitlines()
    print(f"==================== CELL {idx} DIFF ====================")
    for l in difflib.unified_diff(s2, s1, fromfile="8p8w-selesai", tofile="4.4-sk1", lineterm=""):
        print(l)
