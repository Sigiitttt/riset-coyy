import json

nb = json.load(open("kode/4_Spark_on_Yarn/4.4-ringkas-optimasi/4-4-irisan-ringkas-optimasi-2p8w-selesai.ipynb", encoding="utf-8"))
c20 = "".join(nb["cells"][20]["source"])
print("=== Cell 20 in 4-4-irisan-ringkas-optimasi-2p8w-selesai.ipynb ===")
print("\n".join(c20.splitlines()[:20]))

# Check cell 31 (evaluation output)
c31 = nb["cells"][31]
print("\n=== Cell 31 outputs ===")
for out in c31.get("outputs", []):
    if out.get("output_type") == "stream":
        print("".join(out.get("text", []))[:500])
