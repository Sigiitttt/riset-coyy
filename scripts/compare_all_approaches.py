import json
import os

files = {
    "teman_01": "01_audit_dedup.ipynb",
    "teman_02": "02_leakage_labels.ipynb",
    "irisan_md5_clau": "kode/3_jalur_irisan_3kelas/irisan-md5hash-clau.ipynb",
    "irisan_md5_phash": "kode/3_jalur_irisan_3kelas/irisan_mapping md5_phash.ipynb",
    "irisan_improve": "kode/3_jalur_irisan_3kelas/irisan_mapping improve.ipynb",
    "biner_improve": "kode/2_jalur_biner/binary_mapping improve.ipynb"
}

for name, path in files.items():
    print("=" * 80)
    print(f"FILE: {name} -> {path}")
    print("=" * 80)
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    print(f"Total cells: {len(nb['cells'])}")
    for i, cell in enumerate(nb['cells']):
        src = "".join(cell.get("source", []))
        cell_type = cell.get("cell_type")
        lines = [l.strip() for l in src.split("\n") if l.strip()]
        first_line = lines[0] if lines else ""
        # Look for interesting cells
        if cell_type == "markdown":
            if any(h in first_line for h in ["#", "Langkah", "Audit", "Tujuan", "Hasil", "Kesimpulan", "Ringkasan"]):
                print(f"  Cell {i:2d} [MD]: {first_line[:80]}")
        elif cell_type == "code":
            # check outputs or key variables
            outputs = cell.get("outputs", [])
            out_texts = []
            for out in outputs:
                if "text" in out:
                    out_texts.extend(out["text"])
                elif "data" in out and "text/plain" in out["data"]:
                    out_texts.extend(out["data"]["text/plain"])
            out_summary = " ".join([o.strip() for o in out_texts[:3]])
            if any(k in src.lower() for k in ["md5", "phash", "priority", "hash", "leakage", "overlap", "split", "stratified", "duplicate", "dedup"]):
                print(f"  Cell {i:2d} [CODE]: {first_line[:60]} | Output: {out_summary[:70]}")
