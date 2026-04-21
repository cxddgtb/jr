import akshare as ak
import pandas as pd
import time
from pathlib import Path
from loguru import logger
from .resolver import resolve_code_type

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def fetch_market_data(symbol: str, days: int = 250) -> pd.DataFrame:
    cache_path = CACHE_DIR / f"{symbol}.csv"
    now = pd.Timestamp.now()
    if cache_path.exists() and (now - pd.Timestamp.fromtimestamp(cache_path.stat().st_mtime)).total_seconds() < 3600:
        return pd.read_csv(cache_path, parse_dates=["date"])
        
    asset_type = resolve_code_type(symbol)
    for attempt in range(4):
        try:
            time.sleep(0.8 + attempt * 0.4)
            if asset_type == "etf":
                df = ak.fund_etf_fund_daily_em(symbol=symbol)
                df = df.rename(columns={"日期": "date", "收盘": "close", "最高": "high", "最低": "low", "成交量": "volume"})
            elif asset_type == "open_fund":
                df = ak.fund_open_fund_info_em(symbol=symbol, indicator="单位净值走势")
                df = df.rename(columns={"净值日期": "date", "单位净值": "close"})
                df["high"], df["low"], df["volume"] = df["close"], df["close"], 0
            else:
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
                df = df.rename(columns={"日期": "date", "收盘": "close", "最高": "high", "最低": "low", "成交量": "volume"})
                
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").tail(days).dropna(subset=["close"])
            df["pct"] = df["close"].pct_change()
            df["has_volume"] = (df["volume"] > 1000).any()
            df.to_csv(cache_path, index=False)
            logger.info(f"✅ 成功获取 {symbol} ({asset_type}) | {len(df)} 条")
            return df
        except Exception as e:
            logger.warning(f"🌐 第{attempt+1}次请求 {symbol} 失败: {e}")
    logger.error(f"❌ {symbol} 数据获取彻底失败")
    return pd.DataFrame(columns=["date", "close", "high", "low", "volume", "pct", "has_volume"])
