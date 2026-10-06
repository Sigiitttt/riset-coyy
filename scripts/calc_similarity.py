import json
import difflib
from pathlib import Path

f1 = Path(r"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb")
f2 = Path(r"4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb")

nb1 = json.load(open(f1, encoding="utf-8"))
nb2 = json.load(open(f2, encoding="utf-8"))

cells1 = nb1["cells"]
cells2 = nb2["cells"]

print(f"Total cells: File 4.4 = {len(cells1)}, File 8p8w-selesai = {len(cells2)}")

# 1. Check uint8 in File 4.4
uint8_mentions = []
for i, c in enumerate(cells1):
    src = "".join(c.get("source", []))
    if "uint8" in src:
        uint8_mentions.append(i)
print(f"Cells mentioning uint8 in File 4.4: {uint8_mentions}")

# 2. Cell by cell comparison
identical_cells = 0
different_cells = []
all_results = []

for i in range(max(len(cells1), len(cells2))):
    c1 = cells1[i] if i < len(cells1) else None
    c2 = cells2[i] if i < len(cells2) else None

    if c1 is None:
        all_results.append((i, "Extra in 8p8w", "", "Exists", 0.0))
        different_cells.append(i)
        continue
    if c2 is None:
        all_results.append((i, "Extra in 4.4", "Exists", "", 0.0))
        different_cells.append(i)
        continue

    src1 = "".join(c1.get("source", []))
    src2 = "".join(c2.get("source", []))

    matcher = difflib.SequenceMatcher(None, src1, src2)
    ratio = matcher.ratio()

    if src1.strip() == src2.strip():
        identical_cells += 1
        all_results.append((i, c1["cell_type"], "IDENTIK", "IDENTIK", 100.0))
    else:
        different_cells.append(i)
        all_results.append((i, c1["cell_type"], src1[:50], src2[:50], ratio * 100))

total_cells = max(len(cells1), len(cells2))
cell_similarity_pct = (identical_cells / total_cells) * 100

# Total text similarity ratio
full_text1 = "\n".join("".join(c.get("source", [])) for c in cells1)
full_text2 = "\n".join("".join(c.get("source", [])) for c in cells2)
full_ratio = difflib.SequenceMatcher(None, full_text1, full_text2).ratio() * 100

print(f"\nIdentical cells: {identical_cells} / {total_cells} ({cell_similarity_pct:.2f}%)")
print(f"Full text sequence similarity: {full_ratio:.2f}%")
print(f"Different cells: {different_cells}")

for i, ctype, s1, s2, pct in all_results:
    if pct < 100.0:
        print(f"Cell {i:02d} ({ctype}): {pct:.1f}% match")
        d = difflib.unified_diff(src2.splitlines(), src1.splitlines(), fromfile="8p8w", tofile="4.4")
        print("\n".join(list(d)[:20]))
