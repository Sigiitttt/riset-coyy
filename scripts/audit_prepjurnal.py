import json
import ast
import re

nb_path = 'kode/4_Spark_on_Yarn/4.6-ringkas-optimasi-prepjurnal/sk1-irisan-tipe1-ringkas-prepjurnal.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")

defined_vars = set()
used_vars = set()
syntax_errors = []

for idx, cell in enumerate(nb['cells']):
    ctype = cell['cell_type']
    src = ''.join(cell['source'])
    lines = src.splitlines()
    first_line = lines[0] if lines else 'EMPTY'
    print(f"[{idx:02d}] ({ctype:8s}): {first_line[:75]}")

    if ctype == 'code':
        # Check python AST
        clean_lines = [l for l in lines if not l.strip().startswith('!') and not l.strip().startswith('%')]
        clean_code = '\n'.join(clean_lines)
        try:
            tree = ast.parse(clean_code)
        except SyntaxError as e:
            syntax_errors.append((idx, str(e)))

print("\n--- SYNTAX ERRORS ---")
print(syntax_errors if syntax_errors else "None! 100% clean.")
