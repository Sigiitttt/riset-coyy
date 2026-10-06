import json
import ast
from pathlib import Path

nb_path = Path("kode/4_Spark_on_Yarn/4.7-finetune-conv5/sk1-irisan-tipe1-finetune-conv5.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code":
        src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        lines = [l for l in src.splitlines(True) if not l.strip().startswith("!") and not l.strip().startswith("%")]
        # Also handle IPython magics or bash lines if any
        clean_code = "".join(lines)
        try:
            ast.parse(clean_code)
            # print(f"Cell {i}: OK")
        except Exception as e:
            print(f"Cell {i} error: {e}")
            first_lines = clean_code.splitlines()[:5]
            print("  First lines:", first_lines)
