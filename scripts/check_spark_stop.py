import json

nb = json.load(open(r"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb", encoding="utf-8"))

c25 = "".join(nb["cells"][25]["source"])

print("Lines mentioning spark in Cell 25:")
for l in c25.splitlines():
    if "spark" in l.lower() or "stop" in l.lower():
        print("  ", l)

print("\nLast 15 lines of Cell 25:")
for l in c25.splitlines()[-15:]:
    print("  ", l)
