import json

for fname in ["sk1-irisan-tipe1-ringkas-optimasi.ipynb", "sk2-biner-tipe1-ringkas-optimasi.ipynb"]:
    nb = json.load(open(f"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/{fname}", encoding="utf-8"))
    print(f"================== {fname} ==================")
    c16 = "".join(nb["cells"][16]["source"])
    c19 = "".join(nb["cells"][19]["source"])
    c20 = "".join(nb["cells"][20]["source"])
    c24 = "".join(nb["cells"][24]["source"])
    print("--- Cell 16 first line:", c16.splitlines()[0] if c16 else "empty")
    print("--- Cell 19 pip install line:", [l for l in c19.splitlines() if "pip install" in l])
    print("--- Cell 20 first 3 lines:\n", "\n".join(c20.splitlines()[:3]))
    print("--- Cell 24 has auto-split fallback?:", "Auto-split siap" in c24)
