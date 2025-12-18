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

# ========================= Tool 1: URL 内容读取 =========================
@tool
def read_url(url: str, max_chars: int = 1500) -> str:
    """Read and return text content from a web page."""
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    text = r.text.replace("\n", " ")
    return text[:max_chars]

# ========================= Tool 2: CSV 分析 =========================
@tool 
def analyze_csv(file_path: str, max_rows: int = 5) -> str:
    """Analyze a local CSV file."""
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"

    df = pd.read_csv(file_path)
    return (
        f"Shape: {df.shape}\n"
        f"Columns: {list(df.columns)}\n\n"
        f"Head:\n{df.head(max_rows).to_string(index=False)}"
    )

# ========================= Tool 3: tushare 行情 =========================
@tool 
def download_stock_price(
    Ashare_code: str,
    end_date: str,
    days: int = 10,
    file_path: str = "data",
    file_name: str = "stock_data.csv"
) -> str:
    """
    Download last N trading days of stock price using Tushare,
    save to CSV in specified folder with specified file name.
    
    Parameters:
    - Ashare_code: Stock code, e.g., '600519.SH'
    - end_date: End date in 'YYYYMMDD', e.g., '20251217'
    - days: Number of trading days to download
    - file_path: Folder to save CSV, default './data'
    - file_name: CSV file name, e.g., '600519.csv'
    
    Returns:
    - str: Saved file path or error message
    """
    if not TuShare_API:
        return "TUSHARE_TOKEN not set."

    # 初始化 Tushare
    ts.set_token(TuShare_API)
    pro = ts.pro_api()

    # 下载数据
    try:
        df = pro.daily(ts_code=Ashare_code, end_date=end_date, limit=days)
    except Exception as e:
        return f"Error downloading data: {e}"

    if df.empty:
        return "No data returned."

    # 按交易日期排序
    df = df.sort_values("trade_date")

    # 只保留指定列
    df = df[["trade_date", "open", "high", "low", "close", "vol"]]

    # 创建保存目录
    os.makedirs(file_path, exist_ok=True)
    save_path = os.path.join(file_path, file_name)

    try:
        df.to_csv(save_path, index=False)
    except Exception as e:
        return f"Error saving file: {e}"

    return f"Data saved to {save_path}"

# ========================= Agent 初始化 =========================
def main():
    llm = ChatOpenAI(
        model="glm-4.5-air",
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
        temperature=0,
    )

    agent = create_agent(
        tools=[read_url,analyze_csv, download_stock_price],
        model=llm,
        system_prompt =  "你是一个会编程的金融分析专家，在必要的时候可以使用为你提供的tools",
    )

    prompt = """
    有三个任务：
    1. 用100字的内容总结网页: https://finance.eastmoney.com/a/202512173594061460.html
    2. 用100字的分析CSV file: ./data/daily_prices_sse_50.csv
    3. 下载20251217之前20天的股票数据到当前路径的data文件夹，股票代码600519.SH，保存文件命名为: "股票代码_最后日期.CSV"
    """

    result = agent.invoke({
        "messages": [
        {"role": "user", "content": prompt}
    ]})

    print("\n===== FINAL OUTPUT =====\n")
    print(result)

if __name__ == "__main__":
    main()
