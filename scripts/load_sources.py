from pathlib import Path
import csv
import argparse
import pandas as pd
from sqlalchemy import create_engine, text
from pymongo import MongoClient

BASE = Path(__file__).resolve().parent.parent / "data"

def load_mysql():
    engine = create_engine(
        "mysql+pymysql://root:miclave@127.0.0.1:3306/puffer_source"
    )

    with engine.begin() as c:
        c.execute(text("TRUNCATE TABLE video_sent"))

    for chunk in pd.read_csv(
        BASE / "video_sent_sample.csv",
        chunksize=1000
    ):
        chunk = chunk.rename(columns={"time (ns GMT)": "time"})

        chunk.to_sql(
            "video_sent",
            engine,
            if_exists="append",
            index=False,
            method=None,
            chunksize=500
        )

    print("MySQL: video_sent cargado.")

def load_postgres():
    engine = create_engine(
        "postgresql+psycopg://miuser:miclave@127.0.0.1:5432/puffer_source"
    )

    with engine.begin() as c:
        c.execute(text("TRUNCATE TABLE video_acked"))

    for chunk in pd.read_csv(
        BASE / "video_acked_sample.csv",
        chunksize=1000
    ):
        chunk = chunk.rename(columns={"time (ns GMT)": "time"})

        chunk.to_sql(
            "video_acked",
            engine,
            if_exists="append",
            index=False,
            method=None,
            chunksize=500
        )

    print("PostgreSQL: video_acked cargado.")

def load_mongo_collection(client, filename, collection):
    db = client["puffer_source"]
    col = db[collection]
    col.delete_many({})
    batch = []
    with open(BASE / filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convertir campos numéricos comunes cuando sea posible
            for key in ("time", "video_ts", "size"):
                if key in row and row[key] not in ("", None):
                    try:
                        row[key] = int(float(row[key]))
                    except Exception:
                        pass
            if "ssim_index" in row and row["ssim_index"] not in ("", None):
                try:
                    row["ssim_index"] = float(row["ssim_index"])
                except Exception:
                    pass
            batch.append(row)
            if len(batch) >= 5000:
                col.insert_many(batch)
                batch = []
        if batch:
            col.insert_many(batch)

def load_mongo():
    client = MongoClient("mongodb://127.0.0.1:27017")
    load_mongo_collection(client, "video_size_sample.csv", "video_size")
    load_mongo_collection(client, "ssim_sample.csv", "ssim")
    print("MongoDB: video_size y ssim cargados.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["mysql", "postgres", "mongo", "all"], default="all")
    args = ap.parse_args()
    if args.only in ("mysql", "all"):
        load_mysql()
    if args.only in ("postgres", "all"):
        load_postgres()
    if args.only in ("mongo", "all"):
        load_mongo()

if __name__ == "__main__":
    main()
