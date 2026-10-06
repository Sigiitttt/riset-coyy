import json

nb = json.load(open(r"4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb", encoding="utf-8"))

target_cells = [4, 12, 13, 14, 19, 21, 24, 25, 28, 29, 30, 31, 33]

for idx in target_cells:
    c = nb["cells"][idx]
    # find previous markdown header
    prev_md = ""
    for j in range(idx - 1, -1, -1):
        if nb["cells"][j]["cell_type"] == "markdown":
            prev_md = "".join(nb["cells"][j]["source"]).strip().splitlines()[0]
            break
    src = "".join(c["source"]).strip()
    first_few_lines = "\n".join(src.splitlines()[:4])
    print(f"=== CELL {idx} ===")
    print(f"Header Terdekat : {prev_md}")
    print(f"Awal Kode :\n{first_few_lines}")
    print("-" * 50)
