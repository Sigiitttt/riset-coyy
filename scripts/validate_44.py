import json, ast
from pathlib import Path

folder = Path("kode/4_Spark_on_Yarn/4.4-ringkas-optimasi")
for f in folder.glob("*.ipynb"):
    with open(f, "r", encoding="utf-8") as fp:
        nb = json.load(fp)
    errs = 0
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
            lines = [l for l in src.splitlines(True) if not l.strip().startswith("!") and not l.strip().startswith("%")]
            try:
                ast.parse("".join(lines))
            except Exception as e:
                errs += 1
                print(f"[{f.name}] Cell {i} error: {e}")
    if errs == 0:
        print(f"[{f.name}] 100% Valid AST ({len(nb['cells'])} cells)")
