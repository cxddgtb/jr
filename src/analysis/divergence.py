def detect_divergence(df):
    """简化但稳健的背离探测(价格与RSI/MACD)"""
    if len(df) < 30: return 0.0
    recent = df.tail(30)
    price_dir = 1 if recent["close"].iloc[-1] > recent["close"].iloc[-5] else -1
    rsi_dir = 1 if recent["rsi"].iloc[-1] > recent["rsi"].iloc[-5] else -1
    macd_dir = 1 if recent["macd"].iloc[-1] > recent["macd"].iloc[-5] else -1
    
    div_score = 0.0
    if price_dir != rsi_dir: div_score += 0.5
    if price_dir != macd_dir: div_score += 0.5
    return div_score
