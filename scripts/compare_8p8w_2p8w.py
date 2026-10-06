import json
import difflib
from pathlib import Path

path_a = Path(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb")
path_b = Path(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.4-ringkas-optimasi\4-4-irisan-ringkas-optimasi-2p8w-selesai.ipynb")

print("Checking existence:")
print(f"File A (8p8w): {path_a.exists()} ({path_a.stat().st_size if path_a.exists() else 0} bytes)")
print(f"File B (2p8w): {path_b.exists()} ({path_b.stat().st_size if path_b.exists() else 0} bytes)")

if not path_a.exists() or not path_b.exists():
    # If file A is somewhere else, search for it
    if not path_a.exists():
        for p in Path(".").glob("*8p8w*"):
            print("Found alternative:", p)
    exit()

with open(path_a, "r", encoding="utf-8") as f:
    nb_a = json.load(f)
with open(path_b, "r", encoding="utf-8") as f:
    nb_b = json.load(f)

cells_a = nb_a.get("cells", [])
cells_b = nb_b.get("cells", [])

print(f"\nTotal cells: File A = {len(cells_a)}, File B = {len(cells_b)}")

code_diffs = []
output_diffs = []

for i in range(max(len(cells_a), len(cells_b))):
    ca = cells_a[i] if i < len(cells_a) else None
    cb = cells_b[i] if i < len(cells_b) else None

    if ca is None:
        code_diffs.append((i, "EXTRA CELL IN FILE B", "", "".join(cb.get("source", []))))
        continue
    if cb is None:
        code_diffs.append((i, "EXTRA CELL IN FILE A", "".join(ca.get("source", [])), ""))
        continue

    type_a = ca.get("cell_type")
    type_b = cb.get("cell_type")

    src_a = "".join(ca.get("source", []))
    src_b = "".join(cb.get("source", []))

    if type_a != type_b:
        code_diffs.append((i, f"TYPE MISMATCH: {type_a} vs {type_b}", src_a, src_b))
    elif src_a.strip() != src_b.strip():
        code_diffs.append((i, "SOURCE DIFFERENCE", src_a, src_b))

    # Check text output differences
    out_a_text = []
    for out in ca.get("outputs", []):
        if "text" in out:
            out_a_text.append("".join(out["text"]))
    out_b_text = []
    for out in cb.get("outputs", []):
        if "text" in out:
            out_b_text.append("".join(out["text"]))

    str_out_a = "".join(out_a_text).strip()
    str_out_b = "".join(out_b_text).strip()

    if str_out_a != str_out_b:
        output_diffs.append((i, str_out_a, str_out_b))

print(f"\nTotal cells with CODE / SOURCE differences: {len(code_diffs)}")
for idx, reason, sa, sb in code_diffs:
    print(f"\n=== CELL {idx}: {reason} ===")
    lines_a = sa.splitlines()
    lines_b = sb.splitlines()
    diff = list(difflib.unified_diff(lines_a, lines_b, fromfile="8p8w (File A)", tofile="2p8w (File B)", lineterm=""))
    print("\n".join(diff[:30]))
    if len(diff) > 30:
        print(f"... ({len(diff) - 30} more diff lines)")

print(f"\n==========================================")
print(f"Total cells with OUTPUT differences: {len(output_diffs)}")
print("Summary of key output differences (metrics, timings, logs):")
for idx, oa, ob in output_diffs:
    print(f"\n--- Output Cell {idx} ---")
    first_a = oa.splitlines()[:3]
    first_b = ob.splitlines()[:3]
    print(f"  File A (8p8w) snippet: {' | '.join(first_a)}")
    print(f"  File B (2p8w) snippet: {' | '.join(first_b)}")
