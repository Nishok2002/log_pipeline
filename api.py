from fastapi import FastAPI
import pandas as pd
from datetime import datetime
import glob, os

app = FastAPI()

def _latest_clean_parquet():
    files = glob.glob("data/clean/*.parquet")
    if not files:
        raise FileNotFoundError("No parquet files in data/clean/")
    return max(files, key=os.path.getmtime)

@app.get("/logins_today")
def logins_today():
    try:
        path = _latest_clean_parquet()
        df = pd.read_parquet(path)
    except FileNotFoundError:
        return {"logins_today": 0}

    today = datetime.today().strftime("%Y-%m-%d")
    mask = df["timestamp"].str.startswith(today) & (df["action"] == "login")
    return {"logins_today": int(mask.sum())}
