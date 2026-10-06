import json

def inspect_notebook(path, out_txt):
    with open(path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    with open(out_txt, 'w', encoding='utf-8') as out:
        for idx, cell in enumerate(nb['cells']):
            out.write(f"=== CELL {idx} ({cell['cell_type']}) ===\n")
            out.write(''.join(cell['source']) + "\n\n")
    print(f"Dumped {len(nb['cells'])} cells to {out_txt}")

if __name__ == '__main__':
    inspect_notebook('kode/7_referensi tugas sebelumnya/sk3-bigdat-data2017-3kelas-ak85.ipynb', 'scratch_sk3_dump.txt')
    inspect_notebook('kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb', 'scratch_prepjurnal_dump.txt')
