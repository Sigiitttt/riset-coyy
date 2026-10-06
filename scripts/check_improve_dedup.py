import pandas as pd
import json

with open("kode/3_jalur_irisan_3kelas/irisan_mapping improve.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Let's inspect cell 6 of irisan_mapping improve.ipynb table output
for c in nb['cells']:
    if c['cell_type'] == 'code' and 'PRIORITY_ORDER' in "".join(c.get('source', [])):
        for o in c.get('outputs', []):
            if 'data' in o and 'text/html' in o['data']:
                print("".join(o['data']['text/html']))
            elif 'text' in o:
                print("".join(o['text']))
