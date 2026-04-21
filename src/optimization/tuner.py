import numpy as np
from loguru import logger
from collections import Counter

def get_error_attribution(errors: list) -> str:
    if not errors: return "模型正常波动"
    cnt = Counter(errors)
    top = cnt.most_common(2)
    return f"{top[0][0]}({top[0][1]}次)" + (f", {top[1][0]}({top[1][1]}次)" if len(top)>1 else "")

def safe_adaptive_tune(cfg: dict, hit_rate: float) -> dict:
    opt, w, t = cfg["optimization"], cfg["weights"].copy(), cfg["thresholds"].copy()
    b, step, alpha = opt["bounds"], opt["adjust_step"], opt["ema_alpha"]
    
    # EMA平滑胜率防抖
    cfg["performance"]["ema_hit_rate"] = alpha * hit_rate + (1 - alpha) * cfg["performance"]["ema_hit_rate"]
    smooth_hr = cfg["performance"]["ema_hit_rate"]
    
    if smooth_hr < 0.58:
        logger.warning("⚠️ 平滑胜率偏低，防御模式")
        w["trend"] = max(b["trend"][0], w["trend"]-step)
        w["volatility"] = min(b["volatility"][1], w["volatility"]+step/2)
        t["buy_conf"] = max(b["buy_conf"][0], t["buy_conf"]+0.015)
    elif smooth_hr > 0.73:
        logger.info("✅ 平滑胜率优良，进攻模式")
        w["trend"] = min(b["trend"][1], w["trend"]+step/2)
        t["buy_conf"] = min(b["buy_conf"][1], t["buy_conf"]-0.015)
        
    s = sum(w.values())
    cfg["weights"] = {k: round(v/s, 3) for k,v in w.items()}
    cfg["thresholds"] = t
    return cfg
