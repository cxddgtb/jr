from collections import Counter
from loguru import logger

def get_error_attribution(errors: list) -> str:
    """
    对历史验证失败的样本进行归类统计，提取主要失效场景
    """
    if not errors:
        return "模型运行稳定，暂无显著误差模式"
        
    # 统计错误类型频次
    cnt = Counter(errors)
    top_errors = cnt.most_common(3)
    
    # 生成归因描述
    attribution = " | ".join([f"{err}({freq}次)" for err, freq in top_errors])
    logger.info(f"🎯 误差归因完成: {attribution}")
    return attribution
