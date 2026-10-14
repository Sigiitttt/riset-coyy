import json
import os
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

nb_path = 'kode/7_Final Riset/Irisan_convnext_tiny_tanpa_spark.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for idx, c in enumerate(nb['cells']):
    exec_c = c.get('execution_count')
    outputs = c.get('outputs', [])
    source = c.get('source', [])
    first_lines = "".join(source[:3]).replace('\n', ' ')
    print(f"--- CELL {idx} ({c['cell_type']}) | exec_count={exec_c} | outputs={len(outputs)} ---")
    print(f"  Code: {first_lines[:90]}")
    if outputs:
        for oi, o in enumerate(outputs):
            otype = o.get('output_type')
            if otype == 'stream':
                text = "".join(o.get('text', []))[:120].replace('\n', ' ')
                print(f"    [out {oi}] stream: {text}")
            elif otype == 'error':
                ename = o.get('ename')
                evalue = o.get('evalue')
                print(f"    [out {oi}] ERROR: {ename}: {evalue}")
            elif otype in ('display_data', 'execute_result'):
                keys = list(o.get('data', {}).keys())
                print(f"    [out {oi}] {otype}: {keys}")
    else:
        print("    (NO OUTPUT)")
