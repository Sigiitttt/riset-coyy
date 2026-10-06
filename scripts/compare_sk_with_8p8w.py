import json
import difflib
from pathlib import Path

ref_path = Path(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\4-4-irisan-ringkas-optimasi-8p8w-selesai.ipynb")
sk1_path = Path(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.4-ringkas-optimasi\sk1-irisan-tipe1-ringkas-optimasi.ipynb")
sk2_path = Path(r"C:\Users\ARII\Downloads\Data Understanding Isic & Ham10k\kode\4_Spark_on_Yarn\4.4-ringkas-optimasi\sk2-biner-tipe1-ringkas-optimasi.ipynb")

with open(ref_path, "r", encoding="utf-8") as f:
    nb_ref = json.load(f)
with open(sk1_path, "r", encoding="utf-8") as f:
    nb_sk1 = json.load(f)
with open(sk2_path, "r", encoding="utf-8") as f:
    nb_sk2 = json.load(f)

def compare_nbs(name_target, nb_target, nb_ref):
    cells_t = nb_target.get("cells", [])
    cells_r = nb_ref.get("cells", [])
    print(f"\n=======================================================")
    print(f"KOMPARASI: {name_target} (total {len(cells_t)} sel) vs 8p8w-selesai (total {len(cells_r)} sel)")
    print(f"=======================================================")
    diffs = []
    for i in range(max(len(cells_t), len(cells_r))):
        ct = cells_t[i] if i < len(cells_t) else None
        cr = cells_r[i] if i < len(cells_r) else None

        if ct is None:
            diffs.append((i, "SEL HANYA ADA DI 8p8w-selesai", "", "".join(cr.get("source", []))))
            continue
        if cr is None:
            diffs.append((i, f"SEL HANYA ADA DI {name_target}", "".join(ct.get("source", [])), ""))
            continue

        st = "".join(ct.get("source", []))
        sr = "".join(cr.get("source", []))

        if st.strip() != sr.strip():
            diffs.append((i, "PERBEDAAN SOURCE", st, sr))

    print(f"Total sel berbeda: {len(diffs)}")
    for idx, reason, st, sr in diffs:
        print(f"\n--- Sel {idx}: {reason} ---")
        lines_t = st.splitlines()
        lines_r = sr.splitlines()
        diff = list(difflib.unified_diff(lines_r, lines_t, fromfile="8p8w-selesai (Ref)", tofile=name_target, lineterm=""))
        print("\n".join(diff[:25]))
        if len(diff) > 25:
            print(f"... ({len(diff) - 25} lines more)")

compare_nbs("sk1-irisan-tipe1-ringkas-optimasi.ipynb", nb_sk1, nb_ref)
compare_nbs("sk2-biner-tipe1-ringkas-optimasi.ipynb", nb_sk2, nb_ref)
