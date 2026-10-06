import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_outputs(path):
    print("="*80)
    print("CHECKING OUTPUTS:", path)
    print("="*80)
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", []))
        outs = cell.get("outputs", [])
        out_txt = ""
        for o in outs:
            if "text" in o:
                out_txt += "".join(o["text"])
            elif "data" in o and "text/plain" in o["data"]:
                out_txt += "".join(o["data"]["text/plain"])
        if out_txt.strip():
            print(f"Cell {i} [{cell.get('cell_type')}]:")
            # print lines that have numbers or key info
            for line in out_txt.split("\n"):
                if any(k in line.lower() for k in ["total", "duplikat", "bersih", "cluster", "train", "val", "test", "irisan", "ham10000", "nv", "mel", "bkl"]):
                    print("  ", line.strip())

check_outputs("kode/3_jalur_irisan_3kelas/irisan-md5hash-clau.ipynb")
check_outputs("kode/3_jalur_irisan_3kelas/irisan_mapping md5_phash.ipynb")
