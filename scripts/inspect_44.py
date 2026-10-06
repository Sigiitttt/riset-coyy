import json
from pathlib import Path
import datetime

folder = Path("kode/4_Spark_on_Yarn/4.4-ringkas-optimasi")
for f in folder.glob("*.ipynb"):
    stat = f.stat()
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    ctime = datetime.datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    size_kb = stat.st_size / 1024
    with open(f, "r", encoding="utf-8") as nb_file:
        nb = json.load(nb_file)
    cells = nb.get("cells", [])
    has_output = any(len(c.get("outputs", [])) > 0 for c in cells if c.get("cell_type") == "code")
    print(f"File: {f.name}")
    print(f"  Size: {size_kb:.1f} KB | Modified: {mtime} | Created: {ctime}")
    print(f"  Total cells: {len(cells)} | Has outputs: {has_output}")
    # find SCENARIO_NAME or key config
    for i, c in enumerate(cells):
        src = "".join(c.get("source", []))
        if "SCENARIO_NAME" in src:
            for l in src.splitlines():
                if "SCENARIO" in l or "NUM_WORKERS" in l or "NUM_PARTITIONS" in l:
                    print(f"    Cell {i}: {l.strip()}")
        if "Dull Razor" in src or "Active Contour" in src or "Snake" in src:
            print(f"    Cell {i} contains Preprocessing Mention: {src.splitlines()[0][:60]}")
    print("-" * 50)
