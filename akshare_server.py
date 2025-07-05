from fastmcp import FastMCP
from pydantic import BaseModel
import akshare as ak
import json
from typing import Optional
import sys  # 添加系统模块用于命令行参数处理

# 初始化MCP服务器
mcp = FastMCP(name="financial-report-server")


# 注册财报获取工具
# @mcp.tool()
def get_financial_report(stock_code: str, report_type: str, period_type: str, period: int) -> str:
    """
    获取港股财务报表数据并返回JSON格式字符串
    
    参数:
    stock_code (str): 股票代码，如00700
    report_type (str): 报表类型，可选'income'（利润表）、'balance'（资产负债表）、'cash'（现金流量表）
    period_type (str): 期数类型，'year'（年报）、'report'（报告期，含半年报和季报）
    period (str): 期数，格式为YYYY（年报）或YYYYH1/H2（半年报）或YYYYQ1/Q2/Q3/Q4（季报）
    
    返回:
    str: JSON格式的财务报表数据
    """
    try:
        # 映射报表类型
        report_type_map = {
            'income': '利润表',
            'balance': '资产负债表',
            'cash': '现金流量表'
        }
        
        # 映射期数类型
        period_type_map = {
            'year': '年报',
            'report': '报告期'
        }
        
        # 检查参数有效性
        if report_type not in report_type_map:
            raise ValueError(f"不支持的报表类型: {report_type}，可选值为'income'、'balance'、'cash'")
        
        if period_type not in period_type_map:
            raise ValueError(f"不支持的期数类型: {period_type}，可选值为'year'、'report'")
        
        # 获取财务报表数据
        df = ak.stock_financial_hk_report_em(
            stock=stock_code, 
            symbol=report_type_map[report_type],
            indicator=period_type_map[period_type],
        )
        
        # 处理空数据
        if df is None or df.empty:
            return json.dumps({"error": "未获取到数据", "code": 404}, ensure_ascii=False)
        
        df = df.head(period)
        # 转换为JSON字符串
        return df.to_json(orient='records', force_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"获取财务报表数据失败: {str(e)}", "code": 500}, ensure_ascii=False)

def get_financial_indicators(stock_code: str, period: str) -> str:
    """
    获取港股财务分析指标并返回JSON格式字符串
    
    参数:
    stock_code (str): 股票代码，如00700
    period (str): 期数，格式为YYYY（年报）或YYYYH1/H2（半年报）或YYYYQ1/Q2/Q3/Q4（季报）
    
    返回:
    str: JSON格式的财务分析指标数据
    """
    try:
        # 获取财务分析指标数据
        df = ak.stock_financial_hk_analysis_indicator_em(
            stock=stock_code,
            period=period
        )
        
        # 处理空数据
        if df is None or df.empty:
            return json.dumps({"error": "未获取到数据", "code": 404}, ensure_ascii=False)
        
        # 转换为JSON字符串
        return df.to_json(orient='records', force_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"获取财务分析指标失败: {str(e)}", "code": 500}, ensure_ascii=False)


def test_report_fetching():
    test_cases = [
        # 测试用例: (股票代码, 报表类型, 期数, 周期类型, 预期状态)
        ("00700", "income", 3, "year", "success"),    # 腾讯控股年度利润表
    ]
    
    print("===== 开始接口测试 =====\n")
    
    for i, (stock_code, report_type, periods, period_type, expected_status) in enumerate(test_cases, 1):
        print(f"测试用例 {i}/{len(test_cases)}:")
        print(f"参数: 股票代码={stock_code}, 报表类型={report_type}, 期数={periods}, 周期类型={period_type}")
        
        # 调用接口
        result_str = get_financial_report(stock_code, report_type, period_type, periods)
        result = json.loads(result_str)
        
        # 验证结果
        status = result.get("status")
        if status == expected_status:
            print(f"✅ 测试通过: 状态符合预期 ({status})")
            if status == "success":
                print(f"  返回数据条数: {len(result.get('data', []))}")
        else:
            print(f"❌ 测试失败: 预期状态 {expected_status}, 实际状态 {status}")
            print(f"  错误信息: {result.get('message', '无')}")


# 启动服务器
if __name__ == "__main__":
    # mcp.run(transport="sse", host="0.0.0.0",port=8000)
    test_report_fetching()

# 添加测试函数

        