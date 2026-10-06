import json

nb = json.load(open(r"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb", encoding="utf-8"))
c21 = "".join(nb["cells"][21]["source"])
print(c21[:800])
