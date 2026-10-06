from pathlib import Path
import datetime

for p in sorted(Path("kode").rglob("*.ipynb")):
    stat = p.stat()
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{mtime} | {p}")
