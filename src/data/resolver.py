import re, json
from pathlib import Path
from loguru import logger

CACHE_META = Path("data/cache/metadata.json")
CACHE_META.parent.mkdir(parents=True, exist_ok=True)

def _load_meta() -> dict:
    return json.loads(CACHE_META.read_text()) if CACHE_META.exists() else {}

def _save_meta(meta: dict):
    CACHE_META.write_text(json.dumps(meta, indent=2, ensure_ascii=False))

def resolve_code_type(symbol: str) -> str:
    symbol = symbol.strip()
    if not re.match(r"^\d{6}$", symbol):
        raise ValueError(f"❌ 仅支持6位纯数字代码: {symbol}")
    meta = _load_meta()
    if symbol in meta: return meta[symbol]
    
    import akshare as ak
    for t in ["etf", "open_fund", "stock_a"]:
        try:
            df = ak.fund_etf_fund_daily_em(symbol=symbol).head(1) if t=="etf" else \
                 ak.fund_open_fund_info_em(symbol=symbol, indicator="单位净值走势").head(1) if t=="open_fund" else \
                 ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq").head(1)
            if not df.empty:
                meta[symbol] = t; _save_meta(meta)
                logger.info(f"🔍 识别成功: {symbol} -> {t}")
                return t
        except: continue
    raise RuntimeError(f"❌ {symbol} 未匹配到可用数据源，请检查代码或网络")
