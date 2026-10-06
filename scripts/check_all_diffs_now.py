import json
import difflib
from pathlib import Path

path_a = Path(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb")
path_b = Path(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.4-ringkas-optimasi\4-4-irisan-ringkas-optimasi-2p8w-selesai.ipynb")

with open(path_a, "r", encoding="utf-8") as f:
    nb_a = json.load(f)
with open(path_b, "r", encoding="utf-8") as f:
    nb_b = json.load(f)

cells_a = nb_a.get("cells", [])
cells_b = nb_b.get("cells", [])

print(f"Total cells: File A = {len(cells_a)}, File B = {len(cells_b)}")

code_diffs = []

for i in range(max(len(cells_a), len(cells_b))):
    if i >= len(cells_a):
        code_diffs.append((i, "EXTRA CELL IN FILE B", "", "".join(cells_b[i].get("source", []))))
        continue
    if i >= len(cells_b):
        code_diffs.append((i, "EXTRA CELL IN FILE A", "".join(cells_a[i].get("source", [])), ""))
        continue

    ca = cells_a[i]
    cb = cells_b[i]

    type_a = ca.get("cell_type")
    type_b = cb.get("cell_type")

    src_a = "".join(ca.get("source", []))
    src_b = "".join(cb.get("source", []))

    if type_a != type_b:
        code_diffs.append((i, f"TYPE MISMATCH: {type_a} vs {type_b}", src_a, src_b))
    elif src_a.strip() != src_b.strip():
        code_diffs.append((i, "SOURCE CODE BERBEDA", src_a, src_b))

print(f"\nJumlah sel dengan perbedaan KODE: {len(code_diffs)}")
for idx, reason, sa, sb in code_diffs:
    print(f"\n==========================================")
    print(f"SEL {idx}: {reason}")
    print(f"==========================================")
    diff = list(difflib.unified_diff(sa.splitlines(), sb.splitlines(), fromfile="File A (8p8w)", tofile="File B (2p8w)", lineterm=""))
    print("\n".join(diff))
