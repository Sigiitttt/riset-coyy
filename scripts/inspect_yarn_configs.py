import json
import sys

nb1 = json.load(open(r"kode/4-4-irisan-ringkas-optimasi-8p2w-selesai.ipynb", encoding="utf-8"))
nb2 = json.load(open(r"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb", encoding="utf-8"))

for name, nb in [("8p2w-selesai", nb1), ("sk1-in-4.4", nb2)]:
    print(f"=== {name} ===")
    c11 = "".join(nb["cells"][11]["source"]).encode("ascii", "replace").decode("ascii")
    c12 = "".join(nb["cells"][12]["source"]).encode("ascii", "replace").decode("ascii")
    c14 = "".join(nb["cells"][14]["source"]).encode("ascii", "replace").decode("ascii")
    print("Cell 11:\n", c11)
    print("Cell 14:\n", c14)
    print("=" * 50)
