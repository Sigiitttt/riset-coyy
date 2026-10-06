import json, ast
from pathlib import Path

target_file = Path(r"4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb")
with open(target_file, "r", encoding="utf-8") as f:
    nb = json.load(f)

errs = 0
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code":
        src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        lines = [l for l in src.splitlines(True) if not l.strip().startswith("!") and not l.strip().startswith("%")]
        # Also skip shell continuation lines if any
        clean_lines = []
        skip_next = False
        for l in lines:
            if skip_next:
                if not l.strip().endswith("\\"):
                    skip_next = False
                continue
            if l.strip().startswith("!") and l.strip().endswith("\\"):
                skip_next = True
                continue
            clean_lines.append(l)
        try:
            ast.parse("".join(clean_lines))
        except Exception as e:
            errs += 1
            print(f"Cell {i} error: {e}")

if errs == 0:
    print("ALL CODE CELLS IN BERKAS A 100% VALID AST!")
