import json
import difflib

nb_a = json.load(open(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb", encoding="utf-8"))
nb_b = json.load(open(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.4-ringkas-optimasi\4-4-irisan-ringkas-optimasi-2p8w-selesai.ipynb", encoding="utf-8"))

print("=== CELL 19 DIFFERENCE IN DETAIL ===")
sa = "".join(nb_a["cells"][19]["source"])
sb = "".join(nb_b["cells"][19]["source"])
for l in difflib.unified_diff(sa.splitlines(), sb.splitlines(), fromfile="8p8w", tofile="2p8w", lineterm=""):
    print(l)

print("\n=== CELL 30 (TEST EVALUATION) COMPARISON ===")
def get_text(cell):
    res = []
    for o in cell.get("outputs", []):
        if "text" in o: res.append("".join(o["text"]))
    return "".join(res)

print("--- File A (8p8w) Output ---")
print(get_text(nb_a["cells"][30]))

print("--- File B (2p8w) Output ---")
print(get_text(nb_b["cells"][30]))

print("\n=== CELL 33 & 34 in File A vs File B ===")
print("File A cell 32 type:", nb_a["cells"][32]["cell_type"])
print("File A cell 33 type:", nb_a["cells"][33]["cell_type"], "Length source:", len("".join(nb_a["cells"][33]["source"])))
print("File A cell 34 type:", nb_a["cells"][34]["cell_type"], "Length source:", len("".join(nb_a["cells"][34]["source"])))

print("File B cell 32 type:", nb_b["cells"][32]["cell_type"])
print("File B cell 33 type:", nb_b["cells"][33]["cell_type"], "Length source:", len("".join(nb_b["cells"][33]["source"])))
print("File B cell count:", len(nb_b["cells"]))
