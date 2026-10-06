import json

f1 = r"kode/4-4-irisan-ringkas-optimasi-8p2w-selesai.ipynb"
f2 = r"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb"

nb1 = json.load(open(f1, encoding="utf-8"))
nb2 = json.load(open(f2, encoding="utf-8"))

for idx in [20, 21, 22, 24, 25, 26, 28, 30]:
    s1 = "".join(nb1["cells"][idx]["source"]).strip()
    s2 = "".join(nb2["cells"][idx]["source"]).strip()
    match = (s1 == s2)
    print(f"Cell {idx}: Identical = {match}")
    if not match:
        print(f"  Length s1: {len(s1)}, s2: {len(s2)}")
