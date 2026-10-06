import json

nb = json.load(open('kode/4_Spark_on_Yarn/4.7-finetune-conv5/sk1-irisan-tipe1-finetune-conv5.ipynb', encoding='utf-8'))
for i in [26, 27, 28, 29]:
    print(f"=== Cell {i} ({nb['cells'][i]['cell_type']}) ===")
    src = "".join(nb['cells'][i]['source'])
    print(src[:600])
    print()
