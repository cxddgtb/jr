import json, datetime
from pathlib import Path
import akshare as ak
import pandas as pd
from loguru import logger
from src.data.resolver import resolve_code_type

def verify_historical_predictions(cfg: dict, archive_dir: Path) -> tuple[float, float, list[str]]:
    lag = cfg["optimization"]["verification_lag_days"]
    archives = sorted(archive_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    min_s = cfg["optimization"]["min_valid_samples"]
    
    if len(archives) < min_s: return 0.5, 1.0, ["样本积累中"]
        
    hits, wins, losses, errors = 0, 0, 0, []
    for f in archives[:cfg["optimization"]["rolling_window"]]:
        try:
            rec = json.loads(f.read_text())
            pred_date = pd.Timestamp(rec["timestamp"].split("T")[0])
            if (pd.Timestamp.now() - pred_date).days < lag: continue
            
            symbol = rec["symbol"]
            try:
                t = resolve_code_type(symbol)
                getter = ak.fund_etf_fund_daily_em if t=="etf" else ak.fund_open_fund_info_em if t=="open_fund" else ak.stock_zh_a_hist
                df = getter(symbol=symbol, indicator="单位净值走势") if t=="open_fund" else getter(symbol=symbol, period="daily", adjust="qfq")
                dcol, pcol = ("净值日期","单位净值") if t=="open_fund" else ("日期","收盘")
                df[dcol] = pd.to_datetime(df[dcol]); df = df.sort_values(dcol)
                idx1 = df[df[dcol]<=pred_date].index[-1]
                idx2 = df[df[dcol]<=pred_date+pd.Timedelta(days=lag+2)].index[-1]
                actual_ret = df.loc[idx2, pcol]/df.loc[idx1, pcol] - 1
            except: continue
                
            actual_t = "看涨" if actual_ret>0.01 else "看跌" if actual_ret<-0.01 else "震荡"
            if actual_t == rec["pred_trend"]:
                hits += 1
                wins += abs(actual_ret)
            else:
                losses += abs(actual_ret)
                errors.append(f"{rec['pred_trend']}误判为{actual_t}")
        except: continue
        
    hit_rate = hits / max(hits + losses, 1)
    profit_factor = wins / max(losses, 0.01)
    return round(hit_rate, 3), round(profit_factor, 2), errors
