from fastmcp import FastMCP
import yfinance as yf
import pandas as pd
from typing import Literal, Optional
import json
import akshare as ak

# 初始化MCP服务器
mcp = FastMCP("FinancialReportServer")

@mcp.tool()
def get_stock_financial_statement_akshare(symbol, report_table='income', period_type='annual', period=1):
    """使用akshare获取股票财务报表数据，支持A股和港股

    参数:
        symbol (str): 股票代码，A股格式如'000001.SZ'或'600000.SH'，港股格式如'00700.HK'
        report_table (str): 报表类型，可选值: 'income' (利润表), 'balance' (资产负债表), 'cash' (现金流量表)
        period_type (str): 财报周期，可选值: 'annual' (年度), 'quarterly' (季度)
        period (int): 获取最近几期的数据，默认为1
    """

    hk_report_type_map = {
        'income': '利润表',
        'balance': '资产负债表',
        'cash': '现金流量表'
    }
    hk_period_map = {
        'annual': '年度',
        'quarterly': '报告期'
    }
    # 验证报表类型和周期参数
    if report_table not in hk_report_type_map:
        return f"无效的报表类型: {report_table}，可选值: income, balance, cash"
    if period_type not in hk_period_map:
        return f"无效的周期类型: {period_type}，可选值: annual, quarterly"

    df = ak.stock_financial_hk_report_em(
        stock=symbol.split('.')[0],  # Reverted parameter name to 'stock' to match API
        symbol=hk_report_type_map[report_table],
        indicator=hk_period_map[period_type]
    )
    
    # Check if data retrieval failed
    if df is None:
        return f"无法获取{symbol}的{hk_report_type_map[report_table]}数据，请检查参数是否正确"
    
    if df.empty:
        return f"未找到{symbol}的{report_table}数据"

    # 取最近period期的数据
    df = df.head(500)
    df.to_csv(symbol + "+" + report_table + "_" + period_type + '.csv')

    result = {
        "stock_code": symbol,
        "report_table": report_table,
        "period_type": period_type,
        "periods": period,
        "data": df.to_dict(orient="records")
    }

    return json.dumps({
        "status": "success", 
        "data": result
    }, ensure_ascii=False)

if __name__ == "__main__":
    # 启动MCP服务器，默认端口8000
    mcp.run(host="0.0.0.0", port=8000, transport="sse")
