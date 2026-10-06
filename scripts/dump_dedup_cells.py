import json

def print_cells(nb_path, cell_indices):
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    print("="*70)
    print("FILE:", nb_path)
    for idx in cell_indices:
        if idx < len(nb["cells"]):
            c = nb["cells"][idx]
            print(f"--- Cell {idx} ({c['cell_type']}) ---")
            print("".join(c["source"]))
            print()

print_cells("kode/3_jalur_irisan_3kelas/irisan_mapping improve.ipynb", [4, 6])
print_cells("kode/2_jalur_biner/binary_mapping improve.ipynb", [4, 8])
