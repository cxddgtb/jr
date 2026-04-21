import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df) < 30: return df
    df = df.copy()
    df["pct"] = df["pct"].clip(-0.15, 0.15)
    df["close"] = df["close"].replace(0, np.nan).ffill()
    if df["has_volume"].any():
        df["volume"] = df["volume"].fillna(0)
    return df.ffill().fillna(0).dropna(subset=["close"])
