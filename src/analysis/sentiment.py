import akshare as ak
from loguru import logger

POS = ["降准", "降息", "利好", "突破", "放量", "资金流入", "政策扶持", "外资加仓", "复苏", "稳增长", "增持"]
NEG = ["加息", "利空", "跌破", "缩量", "监管", "减持", "暴雷", "外资流出", "制裁", "通胀", "违约"]

def get_market_sentiment() -> float:
    try:
        df = ak.stock_news_em(symbol="000001")
        headlines = " ".join(df["标题"].head(15).tolist())
        pos, neg = sum(1 for k in POS if k in headlines), sum(1 for k in NEG if k in headlines)
        return (pos - neg) / max(pos + neg, 1)
    except Exception as e:
        logger.warning(f"📰 情绪抓取降级: {e}"); return 0.0
