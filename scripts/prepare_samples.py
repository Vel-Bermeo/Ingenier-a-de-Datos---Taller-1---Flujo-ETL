from pathlib import Path
import argparse
import pandas as pd

NAMES = [
    "client_buffer",
    "video_sent",
    "video_acked",
    "video_size",
    "ssim",
]

def find_one(folder: Path, prefix: str) -> Path:
    matches = sorted(folder.glob(f"{prefix}_*.csv"))
    if not matches:
        raise FileNotFoundError(f"No encontré un CSV que empiece con {prefix}_ en {folder}")
    return matches[0]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="Carpeta original de Puffer")
    ap.add_argument("--dest", default="../data", help="Carpeta de salida")
    ap.add_argument("--rows", type=int, default=100000, help="Filas por CSV")
    args = ap.parse_args()

    src = Path(args.source)
    dest = (Path(__file__).parent / args.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)

    for prefix in NAMES:
        f = find_one(src, prefix)
        print(f"Leyendo {f.name}...")
        df = pd.read_csv(f, nrows=args.rows)
        out = dest / f"{prefix}_sample.csv"
        df.to_csv(out, index=False)
        print(f"  -> {out} ({len(df):,} filas)")

if __name__ == "__main__":
    main()
