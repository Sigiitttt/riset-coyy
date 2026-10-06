import json
import ast
from pathlib import Path

nb_path = Path("kode/4_Spark_on_Yarn/4.7-finetune-conv5/sk1-irisan-tipe1-finetune-conv5.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for i in [5, 6, 9, 13, 16, 17, 19, 21, 30]:
    c = nb["cells"][i]
    lines = [l for l in c["source"] if not l.strip().startswith("!") and not l.strip().startswith("%")]
    print(f"--- Cell {i} (lines {len(lines)}) ---")
    try:
        ast.parse("".join(lines))
    except Exception as e:
        print(f"Error: {e}")
        # print around line
        if hasattr(e, 'lineno') and e.lineno is not None:
            lno = e.lineno
            start = max(0, lno - 3)
            end = min(len(lines), lno + 3)
            for idx in range(start, end):
                prefix = ">> " if idx + 1 == lno else "   "
                print(f"{prefix}{idx+1}: {lines[idx]}", end="")
        else:
            print("First 5 lines:")
            for l in lines[:5]:
                print(l, end="")
    print()
