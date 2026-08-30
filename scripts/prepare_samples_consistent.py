from pathlib import Path
import argparse
import pandas as pd

CHUNK_SIZE = 200_000

def find_csv(folder: Path, prefix: str) -> Path:
    matches = sorted(folder.glob(f"{prefix}_*.csv"))
    if not matches:
        raise FileNotFoundError(f"No encontré un archivo {prefix}_*.csv en: {folder}")
    return matches[0]

def normalize_index(df):
    if "stream_index" in df.columns and "index" not in df.columns:
        df = df.rename(columns={"stream_index": "index"})
    return df

def take_first_rows(path: Path, n: int) -> pd.DataFrame:
    parts, total = [], 0
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        chunk = normalize_index(chunk)
        need = n - total
        if need <= 0:
            break
        piece = chunk.head(need)
        parts.append(piece)
        total += len(piece)
        if total >= n:
            break
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

def filter_by_streams(path: Path, stream_pairs: set, max_rows: int) -> pd.DataFrame:
    parts, total = [], 0
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        chunk = normalize_index(chunk)
        mask = [(str(s), int(i)) in stream_pairs for s, i in zip(chunk["session_id"], chunk["index"])]
        piece = chunk.loc[mask]
        if not piece.empty:
            need = max_rows - total
            parts.append(piece.head(need))
            total += min(len(piece), need)
        if total >= max_rows:
            break
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

def filter_acked(path: Path, sent_keys: set, max_rows: int) -> pd.DataFrame:
    parts, total = [], 0
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        chunk = normalize_index(chunk)
        mask = [(str(s), int(i), int(v)) in sent_keys
                for s, i, v in zip(chunk["session_id"], chunk["index"], chunk["video_ts"])]
        piece = chunk.loc[mask]
        if not piece.empty:
            need = max_rows - total
            parts.append(piece.head(need))
            total += min(len(piece), need)
        if total >= max_rows:
            break
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

def filter_catalog(path: Path, catalog_keys: set, max_rows: int) -> pd.DataFrame:
    parts, total = [], 0
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        mask = [(str(c), int(v), str(f)) in catalog_keys
                for c, v, f in zip(chunk["channel"], chunk["video_ts"], chunk["format"])]
        piece = chunk.loc[mask]
        if not piece.empty:
            need = max_rows - total
            parts.append(piece.head(need))
            total += min(len(piece), need)
        if total >= max_rows:
            break
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--dest", default=None)
    ap.add_argument("--rows", type=int, default=100000)
    args = ap.parse_args()

    src = Path(args.source)
    dest = Path(args.dest) if args.dest else Path(__file__).resolve().parent.parent / "data"
    dest.mkdir(parents=True, exist_ok=True)

    sent_path = find_csv(src, "video_sent")
    ack_path = find_csv(src, "video_acked")
    buffer_path = find_csv(src, "client_buffer")
    size_path = find_csv(src, "video_size")
    ssim_path = find_csv(src, "ssim")

    print("1/5 Seleccionando video_sent...")
    sent = take_first_rows(sent_path, args.rows)
    sent.to_csv(dest / "video_sent_sample.csv", index=False)

    stream_pairs = {(str(s), int(i)) for s, i in zip(sent["session_id"], sent["index"])}
    sent_keys = {(str(s), int(i), int(v)) for s, i, v in zip(sent["session_id"], sent["index"], sent["video_ts"])}
    catalog_keys = {(str(c), int(v), str(f)) for c, v, f in zip(sent["channel"], sent["video_ts"], sent["format"])}

    print("2/5 Filtrando video_acked...")
    ack = filter_acked(ack_path, sent_keys, args.rows)
    ack.to_csv(dest / "video_acked_sample.csv", index=False)

    print("3/5 Filtrando client_buffer...")
    buf = filter_by_streams(buffer_path, stream_pairs, args.rows)
    buf.to_csv(dest / "client_buffer_sample.csv", index=False)

    print("4/5 Filtrando video_size...")
    size = filter_catalog(size_path, catalog_keys, args.rows)
    size.to_csv(dest / "video_size_sample.csv", index=False)

    print("5/5 Filtrando ssim...")
    ssim = filter_catalog(ssim_path, catalog_keys, args.rows)
    ssim.to_csv(dest / "ssim_sample.csv", index=False)

    print("\nMUESTRA TERMINADA")
    print(f"video_sent:   {len(sent):,}")
    print(f"video_acked:  {len(ack):,}")
    print(f"client_buffer:{len(buf):,}")
    print(f"video_size:   {len(size):,}")
    print(f"ssim:         {len(ssim):,}")
    print(f"Salida: {dest}")

if __name__ == "__main__":
    main()
