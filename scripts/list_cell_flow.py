import json

nb = json.load(open(r"4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb", encoding="utf-8"))

for i, c in enumerate(nb["cells"]):
    src = "".join(c["source"])
    first_line = src.splitlines()[0] if src.splitlines() else "EMPTY"
    cell_type = c["cell_type"]
    print(f"Cell {i:02d} [{cell_type:8s}]: {first_line[:75]}")
