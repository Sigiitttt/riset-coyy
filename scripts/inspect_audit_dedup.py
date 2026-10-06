import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_notebook_full(path):
    print("="*80)
    print("INSPECTING:", path)
    print("="*80)
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", []))
        cell_type = cell.get("cell_type")
        print(f"--- Cell {i} ({cell_type}) ---")
        print(src[:400])
        outputs = cell.get("outputs", [])
        for out in outputs:
            if "text" in out:
                txt = "".join(out["text"])
                print("  [OUTPUT]:", txt[:300].strip())
            elif "data" in out and "text/plain" in out["data"]:
                txt = "".join(out["data"]["text/plain"])
                print("  [OUTPUT DATA]:", txt[:300].strip())
        print()

inspect_notebook_full("01_audit_dedup.ipynb")
inspect_notebook_full("02_leakage_labels.ipynb")
