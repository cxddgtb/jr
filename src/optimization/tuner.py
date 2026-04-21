from loguru import logger
import numpy as np

def safe_adaptive_tune(cfg: dict, hit_rate: float) -> dict:
    """
    基于 EMA 平滑胜率与安全边界的自适应调参引擎
    防止参数跳变、过拟合与风格漂移
    """
    opt = cfg["optimization"]
    w = cfg["weights"].copy()
    t = cfg["thresholds"].copy()
    bounds = opt["bounds"]
    step = opt["adjust_step"]
    alpha = opt["ema_alpha"]
    
    # 1. EMA 平滑胜率（防短期噪声干扰）
    prev_ema = cfg["performance"].get("ema_hit_rate", 0.5)
    cfg["performance"]["ema_hit_rate"] = alpha * hit_rate + (1 - alpha) * prev_ema
    smooth_hr = cfg["performance"]["ema_hit_rate"]
    
    # 2. 动态调参逻辑
    if smooth_hr < 0.58:
        logger.warning("⚠️ 平滑胜率偏低，触发防御模式")
        w["trend"] = max(bounds["trend"][0], w["trend"] - step)
        w["volatility"] = min(bounds["volatility"][1], w["volatility"] + step / 2)
        t["buy_conf"] = max(bounds["buy_conf"][0], t["buy_conf"] + 0.015)
    elif smooth_hr > 0.73:
        logger.info("✅ 平滑胜率优良，触发进攻模式")
        w["trend"] = min(bounds["trend"][1], w["trend"] + step / 2)
        t["buy_conf"] = min(bounds["buy_conf"][1], t["buy_conf"] - 0.015)
    else:
        logger.info("🟢 胜率处于稳态区间，参数保持当前配置")
        
    # 3. 权重强制归一化（确保总和=1.0）
    total_w = sum(w.values())
    cfg["weights"] = {k: round(v / total_w, 3) for k, v in w.items()}
    cfg["thresholds"] = t
    
    logger.info(f"🔧 参数已更新: 权重={cfg['weights']} | 置信阈值={cfg['thresholds']['buy_conf']}/{cfg['thresholds']['sell_conf']}")
    return cfg
