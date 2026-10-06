import json
from pathlib import Path

p_8p2w = Path(r"kode/4-4-irisan-ringkas-optimasi-8p2w-selesai.ipynb")
p_44 = Path(r"kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb")
p_root_8w = Path(r"4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb")

print("Checking files:")
print("8p2w exists:", p_8p2w.exists(), p_8p2w.stat().st_size)
print("4.4 exists:", p_44.exists(), p_44.stat().st_size)
print("root 8w exists:", p_root_8w.exists(), p_root_8w.stat().st_size)

with open(p_8p2w, "r", encoding="utf-8") as f:
    nb_8p2w = json.load(f)

print(f"\n--- 8p2w: Total Cells: {len(nb_8p2w['cells'])} ---")
for i in [4, 11, 12, 14, 16, 19, 20, 21, 24, 25, 28, 30, 31]:
    if i < len(nb_8p2w['cells']):
        c = nb_8p2w['cells'][i]
        src = "".join(c.get("source", []))
        first_line = src.splitlines()[0] if src.splitlines() else "EMPTY"
        print(f"Cell {i:02d} ({c['cell_type']}): {first_line[:80]}")
        # check specific lines in cell 4, 11, 14, 19
        if i == 4:
            for l in src.splitlines():
                if any(k in l for k in ["NUM_WORKERS", "NUM_PARTITIONS", "SCENARIO_NAME"]):
                    print(f"    {l.strip()}")
        if i == 11:
            for l in src.splitlines():
                if "YARN_NM" in l:
                    print(f"    {l.strip()}")
        if i == 14:
            for l in src.splitlines():
                if "spark." in l:
                    print(f"    {l.strip()}")
        if i == 19:
            for l in src.splitlines()[:15]:
                print(f"    {l.strip()}")
        # Check outputs of cell 21, 25, 30
        if i in [21, 25, 30, 31]:
            for out in c.get("outputs", []):
                if "text" in out:
                    print(f"    [OUTPUT {i}]: {' '.join(''.join(out['text']).splitlines()[:2])}")
