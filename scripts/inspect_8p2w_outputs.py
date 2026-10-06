import json

nb = json.load(open(r"kode/4-4-irisan-ringkas-optimasi-8p2w-selesai.ipynb", encoding="utf-8"))

for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code" and c.get("outputs"):
        print(f"=== Cell {i} ===")
        for out in c["outputs"]:
            if "text" in out:
                txt = "".join(out["text"])
                for l in txt.splitlines()[:5]:
                    print("  ", l)
