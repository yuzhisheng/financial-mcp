from fastmcp import FastMCP
import yfinance as yf
import pandas as pd
from typing import Literal, Optional
import json

# 初始化MCP服务器
mcp = FastMCP("FinancialReportServer")

# @mcp.tool()
def get_financial_report(
    stock_code: str,
    report_type: Literal["income", "balance", "cashflow"],
    period_type: Literal["yearly", "quarterly"],
    limit: int = 5
) -> str:
    """获取指定股票的财务报表数据，返回JSON格式字符串"""
    try:
        ticker = yf.Ticker(stock_code)

        # 根据报表类型和周期获取数据
        report_map = {
            ("income", "yearly"): ticker.financials,
            ("income", "quarterly"): ticker.quarterly_financials,
            ("balance", "yearly"): ticker.balance_sheet,
            ("balance", "quarterly"): ticker.quarterly_balance_sheet,
            ("cashflow", "yearly"): ticker.cashflow,
            ("cashflow", "quarterly"): ticker.quarterly_cashflow,
        }

        report_data = report_map[(report_type, period_type)]

        # 转置数据并重置索引
        df = report_data.T.reset_index()
        df.columns = ["period"] + list(df.columns[1:])

        # 限制获取的期数
        df = df.head(limit)

        # 转换为字典并处理数值格式
        result = {
            "stock_code": stock_code,
            "report_type": report_type,
            "period_type": period_type,
            "periods": df["period"].tolist(),
            "data": df.drop("period", axis=1).to_dict(orient="records")
        }

        return json.dumps({
            "status": "success", 
            "data": result
        }, ensure_ascii=False)  # ensure_ascii=False保证中文正常显示

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e),
            "hint": "请检查股票代码是否正确，或尝试使用不同的周期类型"
        }, ensure_ascii=False)

if __name__ == "__main__":
    # 启动MCP服务器，默认端口8000
    # mcp.run(host="0.0.0.0", port=8000, transport="sse")
    get_financial_report("APPL", "income", "yearly")