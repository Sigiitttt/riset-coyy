import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("01_audit_dedup.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

for i, cell in enumerate(nb["cells"]):
    src = "".join(cell.get("source", []))
    print(f"=== Cell {i} ({cell.get('cell_type')}) ===")
    print(src[:500])
    for out in cell.get("outputs", []):
        if "text" in out:
            print("  [OUT TEXT]:", "".join(out["text"])[:300].strip())
        elif "data" in out and "text/plain" in out["data"]:
            print("  [OUT PLAIN]:", "".join(out["data"]["text/plain"])[:300].strip())
