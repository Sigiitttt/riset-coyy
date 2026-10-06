import json
from pathlib import Path

nb_path = Path("kode/4_Spark_on_Yarn/4.7-finetune-conv5/sk1-irisan-tipe1-finetune-conv5.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

changed = False
for i, c in enumerate(nb["cells"]):
    if isinstance(c["source"], str):
        c["source"] = c["source"].splitlines(True)
        changed = True

if changed:
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Standardized all cell sources to list of lines.")
else:
    print("All cell sources were already lists.")
