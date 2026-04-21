def classify_regime(df, cfg):
    last = df.iloc[-1]
    t = cfg["thresholds"]
    if last["adx"] > t["adx_trend"]:
        return "strong_uptrend" if last["di_plus"]>last["di_minus"] and last["ma_fast"]>last["ma_long"] else \
               "strong_downtrend" if last["di_minus"]>last["di_plus"] and last["ma_fast"]<last["ma_long"] else "trending_weak"
    elif last["bb_width"] > t["bb_width_high"]: return "high_vol_breakout"
    elif last["bb_width"] < t["bb_width_low"]: return "low_vol_consolidation"
    return "ranging"
