import os
import requests
import pandas as pd
import tushare as ts
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

OPENAI_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
OPENAI_API_KEY = #这里用的glm的apui，需要自己申请
TuShare_API = # 需要自己申请

import sys
import subprocess
from pathlib import Path

#------------------- test mcp -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[0]
file_path = PROJECT_ROOT /"my_tools.py"

# 启动端口
#with open('./trade_tool.log', "w") as f:
#    process = subprocess.Popen([sys.executable, file_path], stdout=f, stderr=subprocess.STDOUT, cwd=os.getcwd())


#------------------- test mcp -------------------------

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

mcp_config = {
            "my_tools": {
                "transport": "streamable_http",
                "url": f"http://localhost:{os.getenv('HTTP_PORT_1', '8000')}/mcp",
            },
            }

# ========================= Agent 初始化 =========================
async def main():

    model = ChatOpenAI(
        model="glm-4.5-air",
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
        temperature=0,
    )

    client = MultiServerMCPClient(mcp_config)

    try:
        my_tools = await client.get_tools() # 尝试连接，http://localhost:8000/mcp
        print(my_tools)
    except Exception as e:
        with open('./trade_tool.log', 'r') as f:
            print(f"连接失败，请检查 trade_tool.log。错误详情: {e}")
        raise e

    agent = create_agent(
        tools=my_tools,
        model=model,
        system_prompt = "你是一个会编程的金融分析专家，在必要的时候可以使用为你提供的tools",
    )

    prompt = """
    有三个任务：
    1. 用100字的内容总结网页: https://finance.eastmoney.com/a/202512173594061460.html
    2. 用100字的分析CSV file: ./data/daily_prices_sse_50.csv
    3. 下载20251217之前20天的股票数据到当前路径的data文件夹，股票代码600519.SH，保存文件命名为: "{股票代码}_{最后日期}.CSV"
    """

    result = await agent.ainvoke({
        "messages": [
        {"role": "user", "content": prompt}
    ]})

    print("\n===== FINAL OUTPUT =====\n")
    print(result)

import asyncio
if __name__ == "__main__":
    asyncio.run(main())

