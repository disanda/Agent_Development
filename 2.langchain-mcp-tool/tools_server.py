import os
import requests
import pandas as pd
import tushare as ts
from fastmcp import FastMCP
import mcp_client

mcp = FastMCP("MyTools")
TuShare_API = mcp_client.TuShare_API

# ========================= Tool 1: URL 内容读取 =========================
@mcp.tool()
def read_url(url: str, max_chars: int = 1500) -> str:
    """Read and return text content from a web page."""
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    text = r.text.replace("\n", " ")
    return text[:max_chars]

# ========================= Tool 2: CSV 分析 =========================
@mcp.tool()
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
@mcp.tool()
def download_stock_price(
    Ashare_code: str,
    end_date: str,
    days: int = 10,
    file_path: str = "data",
    file_name: str = "stock_data.csv",
    TuShare_API: str = TuShare_API
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

if __name__ == "__main__":
    port = int(os.getenv("TRADE_HTTP_PORT", "8000")) # lsof -i :8001，kill PID
    mcp.run(transport="streamable-http", port=port)