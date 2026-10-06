import json

def inspect_notebook(nb_path):
    print("="*60)
    print("Inspecting:", nb_path)
    print("="*60)
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", []))
        cell_type = cell.get("cell_type")
        lines = [l.strip() for l in src.split("\n") if l.strip()]
        first_line = lines[0] if lines else ""
        keywords = ["split", "dedup", "duplikat", "leakage", "harmonisasi", "groupkfold", "stratified", "ham10000", "isic 2017", "isic 2019"]
        if any(k in src.lower() for k in keywords):
            print(f"Cell {i} [{cell_type}]: {first_line[:80]}")

inspect_notebook("kode/3_jalur_irisan_3kelas/irisan_mapping improve.ipynb")
inspect_notebook("kode/2_jalur_biner/binary_mapping improve.ipynb")
