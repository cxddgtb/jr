import datetime

def build_html_report(results: list, cfg: dict, hr: float, pf: float, err: str) -> str:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M CST")
    w, r, perf = cfg["weights"], cfg["risk"], cfg["performance"]
    
    rows = ""
    for x in results:
        color = "#27ae60" if x["trend"]=="看涨" else "#e74c3c" if x["trend"]=="看跌" else "#f39c12"
        rows += f"""
        <tr>
            <td><b>{x['symbol']}</b></td>
            <td>{x['current_price']}</td>
            <td style="color:{color}; font-weight:bold">{x['trend']}</td>
            <td>{x['confidence']}</td>
            <td>{x['regime'].replace('_',' ').title()}</td>
            <td>周:{x['week']} | 月:{x['month']} | 年:{x['year']}</td>
            <td>买:{x['buy_zone'][0]}~{x['buy_zone'][1]}</td>
            <td>止盈:{x['take_profit']} | 止损:{x['stop_loss']}</td>
            <td>{x['position_pct']:.1%}</td>
        </tr>"""
        
    html = f"""
    <html><body style="font-family:Arial,sans-serif; background:#f8f9fa; padding:20px;">
    <h2 style="color:#2c3e50">📊 量化智能分析报告 V7 | {ts}</h2>
    <hr>
    <p>🔍 <b>版本</b>: v{cfg['version']} | 运行: {perf['runs']+1} | 平滑胜率: {perf['ema_hit_rate']:.1%} | 盈亏比: {pf:.2f}</p>
    <p>⚖️ <b>动态权重</b>: 趋势 {w['trend']} | 动量 {w['momentum']} | 量价 {w['volume']} | 波动 {w['volatility']} | 情绪 {w['sentiment']}</p>
    <p>🎯 <b>风控</b>: Kelly仓位≤{r['max_position_pct']:.0%} | ATR止损×{r['atr_stop_mult']} | 目标×{r['atr_target_mult']}</p>
    <table style="width:100%; border-collapse:collapse; margin-top:10px; background:#fff;">
        <tr style="background:#34495e; color:#fff;">
            <th style="padding:8px">标的</th><th>现价</th><th>趋势</th><th>置信</th><th>状态</th><th>周期展望</th><th>买入区</th><th>风控位</th><th>建议仓位</th>
        </tr>
        {rows}
    </table>
    <hr>
    <h3>🤖 自优化与误差诊断</h3>
    <p>• 平滑胜率<58% → 降趋势权重/升波动过滤/提高开多门槛，防御震荡假突破</p>
    <p>• 平滑胜率>73% → 升趋势权重/适度放宽阈值，捕捉主升浪</p>
    <p>• 参数EMA平滑(α=0.3)，防参数跳变与过拟合</p>
    <p>⚠️ <b>风险提示</b>: 本报告为概率推演与风控参考，非确定性交易指令。市场有风险，请严格使用闲钱，执行止损纪律。</p>
    </body></html>
    """
    return html
