import json

p_44 = "kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/sk1-irisan-tipe1-ringkas-optimasi.ipynb"
p_42 = "kode/4_Spark_on_Yarn/4.2-arsip-irisan-benchmark/sk1-irisan-tipe1-ringkas.ipynb"

nb44 = json.load(open(p_44, encoding="utf-8"))
nb42 = json.load(open(p_42, encoding="utf-8"))

print(f"4.4 cells: {len(nb44['cells'])}, 4.2 cells: {len(nb42['cells'])}")

diffs = []
for i in range(min(len(nb44['cells']), len(nb42['cells']))):
    s44 = "".join(nb44['cells'][i]['source'])
    s42 = "".join(nb42['cells'][i]['source'])
    if s44 != s42:
        diffs.append(i)

print(f"Different cells: {diffs}")
for d in diffs:
    print(f"\n--- Cell {d} ({nb44['cells'][d]['cell_type']}) ---")
    s44 = "".join(nb44['cells'][d]['source'])
    s42 = "".join(nb42['cells'][d]['source'])
    print(f"4.4: {s44[:150]}...")
    print(f"4.2: {s42[:150]}...")
