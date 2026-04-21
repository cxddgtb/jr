from .indicators import compute_features
from .regime import classify_regime
from .divergence import detect_divergence
from .sentiment import get_market_sentiment
import numpy as np

def generate_signals(df, cfg):
    df = compute_features(df, cfg)
    last, regime = df.iloc[-1], classify_regime(df, cfg)
    sent = get_market_sentiment()
    w, t, r = cfg["weights"], cfg["thresholds"], cfg["risk"]
    
    # 多维打分(0~1)
    trend_s = np.mean([last["ma_fast"]>last["ma_slow"], last["macd_hist"]>0, last["di_plus"]>last["di_minus"], last["close"]>last["psar"]])
    mom_s = np.mean([last["rsi"]<70, last["rsi"]>30, last["stoch_k"]<80, last["cci"]<100])
    vol_s = min(last["vol_ratio"]/2, 1.0)
    
    # 惩罚与调节
    div_pen = detect_divergence(df) * 0.25
    vol_pen = max(0, (last["hist_vol"] - t["max_daily_vol"]) * 15)
    regime_adj = {"strong_uptrend": 0.06, "strong_downtrend": -0.06}.get(regime, 0)
    
    conf = w["trend"]*trend_s + w["momentum"]*mom_s + w["volume"]*vol_s + w["volatility"]*(1-vol_pen) + w["sentiment"]*((sent+1)/2) - div_pen + regime_adj
    conf = max(0.0, min(1.0, conf))
    
    trend_dir = "看涨" if conf >= t["buy_conf"] else "看跌" if conf <= t["sell_conf"] else "震荡"
    
    # 动态风控 & 仓位
    stop = last["close"] - r["atr_stop_mult"] * last["atr"]
    target = last["close"] + r["atr_target_mult"] * last["atr"]
    kelly = min(r["max_position_pct"], r["kelly_fraction"] * ((conf*1.5) - (1-conf))) if conf>0.5 else 0.0
    
    return {
        "confidence": round(conf, 3), "trend": trend_dir, "regime": regime,
        "week": "偏强" if last["ma_fast"]>last["ma_slow"] else "偏弱",
        "month": "上行" if last["macd"]>0 else "下行",
        "year": "结构性牛市" if trend_dir=="看涨" and last["adx"]>t["adx_trend"] else "防御震荡市",
        "buy_zone": [round(last["bb_lower"], 4), round(last["ma_slow"], 4)],
        "sell_zone": [round(last["bb_upper"], 4), round(last["ma_fast"]*1.05, 4)],
        "stop_loss": round(stop, 4), "take_profit": round(target, 4),
        "position_pct": round(max(0.05, min(kelly, r["max_position_pct"])), 3),
        "atr": round(last["atr"], 4), "hist_vol": round(last["hist_vol"], 4),
        "divergence_flag": bool(div_pen>0.1),
        "current_price": round(last["close"], 4)
    }
