import json
import os
import glob

nb_path = 'kode/7_Final Riset/Irisan_convnext_tiny_tanpa_spark.ipynb'
if os.path.exists(nb_path):
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    print(f"Total cells: {len(nb.get('cells', []))}")
    for idx, cell in enumerate(nb.get('cells', [])):
        cell_type = cell.get('cell_type')
        exec_count = cell.get('execution_count')
        outputs = cell.get('outputs', [])
        source = cell.get('source', [])
        source_line = source[0].strip() if source else ''
        output_types = [o.get('output_type') for o in outputs]
        print(f"Cell {idx} ({cell_type}): exec={exec_count}, outputs={len(outputs)} {output_types} | {source_line[:60]}")

print("\n--- Searching Local History ---")
appdata = os.environ.get('APPDATA', '')
history_dirs = [
    os.path.join(appdata, 'Antigravity', 'User', 'History'),
    os.path.join(appdata, 'Antigravity IDE', 'User', 'History'),
    os.path.join(appdata, 'Code', 'User', 'History')
]

for hdir in history_dirs:
    if os.path.exists(hdir):
        print(f"Checking {hdir}...")
        for root, dirs, files in os.walk(hdir):
            if 'entries.json' in files:
                entries_path = os.path.join(root, 'entries.json')
                try:
                    with open(entries_path, 'r', encoding='utf-8') as ef:
                        data = json.load(ef)
                        resource = data.get('resource', '')
                        if 'Irisan_convnext_tiny_tanpa_spark' in resource:
                            print(f"FOUND MATCH in {entries_path} -> resource: {resource}")
                            entries = data.get('entries', [])
                            for e in entries:
                                print(f"  Entry: id={e.get('id')}, timestamp={e.get('timestamp')}")
                except Exception as ex:
                    pass
