import json

nb44 = json.load(open("kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb", encoding="utf-8"))
c20_44 = "".join(nb44["cells"][20]["source"])
print("=== Cell 20 in 4.4 sk1-irisan-tipe1-ringkas-optimasi.ipynb ===")
print("\n".join(c20_44.splitlines()[:25]))

nb46 = json.load(open("kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb", encoding="utf-8"))
c20_46 = "".join(nb46["cells"][20]["source"])
print("\n=== Cell 20 in 4.6 sk1-irisan-tipe1-ringkas-prepjurnal.ipynb ===")
print("\n".join(c20_46.splitlines()[:25]))
