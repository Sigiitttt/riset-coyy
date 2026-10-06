import json

nb = json.load(open("kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/4-4-irisan-ringkas-optimasi-2p8w-selesai.ipynb", encoding="utf-8"))
for i in [29, 30, 31, 32, 33]:
    if i < len(nb["cells"]):
        c = nb["cells"][i]
        print(f"=== Cell {i} ({c['cell_type']}) ===")
        for out in c.get("outputs", []):
            if out.get("output_type") == "stream":
                print("".join(out.get("text", []))[:400])
