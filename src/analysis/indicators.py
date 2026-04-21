import pandas as pd
import numpy as np
import ta

def compute_features(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    p = cfg["periods"]
    c, h, l, v = df["close"], df["high"], df["low"], df["volume"]
    
    # 趋势
    df["ma_fast"] = ta.trend.sma_indicator(c, p["ma_fast"])
    df["ma_slow"] = ta.trend.sma_indicator(c, p["ma_slow"])
    df["ma_long"] = ta.trend.sma_indicator(c, p["ma_long"])
    df["ema_12"] = ta.trend.ema_indicator(c, 12)
    df["ema_26"] = ta.trend.ema_indicator(c, 26)
    df["psar"] = ta.trend.PSARIndicator(h, l, c).psar()
    
    # 动量
    df["rsi"] = ta.momentum.rsi(c, p["rsi_window"])
    df["stoch_k"] = ta.momentum.stoch(h, l, c, 9, 3)
    df["stoch_d"] = ta.momentum.stoch_signal(h, l, c, 9, 3)
    df["cci"] = ta.trend.cci(h, l, c, 20)
    df["roc"] = ta.momentum.roc(c, 10)
    df["willr"] = ta.momentum.williams_r(h, l, c, 14)
    
    # MACD
    macd = ta.trend.MACD(c, 12, 26, 9)
    df["macd"], df["macd_sig"], df["macd_hist"] = macd.macd(), macd.macd_signal(), macd.macd_diff()
    
    # 波动/风控
    bb = ta.volatility.BollingerBands(c, p["bb_window"], 2)
    df["bb_upper"], df["bb_lower"] = bb.bollinger_hband(), bb.bollinger_lband()
    df["bb_pct"] = (c - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["ma_slow"]
    df["atr"] = ta.volatility.AverageTrueRange(h, l, c, p["atr_window"]).average_true_range()
    df["hist_vol"] = df["pct"].rolling(20).std() * np.sqrt(252)
    df["vol_ratio"] = (v / ta.trend.sma_indicator(v, 20).replace(0, np.nan)) if df["has_volume"].any() else 1.0
    
    # 趋势强度
    adx = ta.trend.ADXIndicator(h, l, c, p["adx_window"])
    df["adx"], df["di_plus"], df["di_minus"] = adx.adx(), adx.adx_pos(), adx.adx_neg()
    
    return df.ffill().fillna(0)
