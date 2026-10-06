import json

nb = json.load(open(r"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb", encoding="utf-8"))
c16 = "".join(nb["cells"][16]["source"])
print(c16[:600])
print("...")
for l in c16.splitlines():
    if "hdfs" in l.lower() or "exists" in l.lower():
        print("  ", l)
