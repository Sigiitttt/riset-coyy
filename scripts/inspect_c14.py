import json
nb = json.load(open("kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/4-4-irisan-ringkas-optimasi-2p8w-selesai.ipynb", encoding="utf-8"))
c14 = nb["cells"][14]
print(c14["cell_type"])
src = "".join(c14["source"])
print(src[:400])
