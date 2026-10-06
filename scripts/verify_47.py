import json
import ast
from pathlib import Path

nb_path = Path("kode/4_Spark_on_Yarn/4.7-finetune-conv5/sk1-irisan-tipe1-finetune-conv5.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")
errors = 0
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code":
        lines = [l for l in c["source"] if not l.strip().startswith("!") and not l.strip().startswith("%")]
        try:
            ast.parse("".join(lines))
        except Exception as e:
            print(f"Cell {i} error: {e}")
            errors += 1

if errors == 0:
    print("ALL CODE CELLS PASSED AST SYNTAX CHECK!")
