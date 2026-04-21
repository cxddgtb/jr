import yaml, json, datetime
from pathlib import Path
from loguru import logger
from src.utils.logger import setup_logger
from src.data.fetcher import fetch_market_data
from src.data.cleaner import clean_data
from src.analysis.signal import generate_signals
from src.optimization.validator import verify_historical_predictions
from src.optimization.tuner import safe_adaptive_tune
from src.optimization.attributor import get_error_attribution
from src.utils.mailer import send_html_report
from src.utils.reporter import build_html_report

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_DIR = ROOT / "data/archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
setup_logger(ROOT)

def run():
    logger.info("🚀 启动 Quant Ultimate V7 流水线")
    with open(ROOT / "config/strategy.yaml") as f: cfg = yaml.safe_load(f)
    symbols = [s.strip() for s in open(ROOT / "config/assets.txt") if s.strip()]
    
    results = []
    for sym in symbols:
        try:
            df = clean_data(fetch_market_data(sym))
            if df.empty or len(df)<30: continue
            sig = generate_signals(df, cfg)
            sig["symbol"] = sym; sig["timestamp"] = datetime.datetime.now().isoformat()
            results.append(sig)
            
            with open(ARCHIVE_DIR / f"{sym}_{datetime.date.today()}.json", "w") as f:
                json.dump({"timestamp": sig["timestamp"], "symbol": sym, "pred_trend": sig["trend"], 
                           "confidence": sig["confidence"], "price": sig["current_price"]}, f, indent=2)
        except Exception as e: logger.error(f"❌ {sym} 处理失败: {e}")
            
    hr, pf, errors = verify_historical_predictions(cfg, ARCHIVE_DIR)
    cfg["performance"].update({"hit_rate": hr, "profit_factor": pf, "runs": cfg["performance"]["runs"]+1})
    cfg = safe_adaptive_tune(cfg, hr)
    with open(ROOT / "config/strategy.yaml", "w") as f: yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)
    
    html = build_html_report(results, cfg, hr, pf, get_error_attribution(errors))
    send_html_report(f"📈 V7 量化智能报告 {datetime.date.today()}", html)
    logger.info("✅ 流水线执行完毕")

if __name__ == "__main__": run()
