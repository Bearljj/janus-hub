import os
import asyncio
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
# 这里的名称会被 AI 识别为工具的前缀 (e.g., local_file_list)
mcp = FastMCP("local-file")

# 受控根目录 (从环境变量或配置中读取)
# 缺省为当前工作目录的 Jupyter 文件夹 (根据之前讨论的设定)
SECURE_ROOT = os.getenv("JANUS_ANALYTICS_DIR", "/Users/harold/working/Jupyter_AI_DataAnalyze")

@mcp.tool()
async def list_files(pattern: str = "*") -> list[str]:
    """
    List files in the secure analytics directory.
    列出安全分析目录下的文件清单。
    """
    import glob
    search_path = os.path.join(SECURE_ROOT, "**", pattern)
    # 仅返回相对路径，保护物理结构 (Privacy First)
    files = glob.glob(search_path, recursive=True)
    return [os.path.relpath(f, SECURE_ROOT) for f in files if os.path.isfile(f)]

@mcp.tool()
async def read_metadata(relative_path: str) -> dict:
    """
    Read file metadata (size, last modified) without loading content.
    读取文件元数据（大小、修改时间），不加载内容。
    """
    full_path = os.path.abspath(os.path.join(SECURE_ROOT, relative_path))
    
    # 路径安全检查 (Path Validation)
    if not full_path.startswith(os.path.abspath(SECURE_ROOT)):
        raise ValueError("Access Denied: Path is outside secure root.")
        
    stat = os.stat(full_path)
    return {
        "size_bytes": stat.st_size,
        "last_modified": stat.st_mtime,
        "extension": os.path.splitext(relative_path)[1]
    }

@mcp.tool()
async def preview_data_schema(relative_path: str, nrows: int = 5) -> str:
    """
    Preview the first few rows of a data file (CSV or Parquet) to understand its schema.
    预览数据文件（CSV 或 Parquet）的前几行以了解其结构。
    """
    full_path = os.path.abspath(os.path.join(SECURE_ROOT, relative_path))
    if not full_path.startswith(os.path.abspath(SECURE_ROOT)):
        raise ValueError("Access Denied")

    import pandas as pd
    ext = os.path.splitext(relative_path)[1].lower()
    
    try:
        if ext == ".parquet":
            # 仅读取头部 (Use engine='fastparquet' or 'pyarrow' if available)
            df = pd.read_parquet(full_path).head(nrows)
        else:
            # 默认为 CSV
            df = pd.read_csv(full_path, nrows=nrows)
        return df.to_markdown()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
async def search_in_file(relative_path: str, query: str) -> str:
    """
    Fast search for a string in a file using grep-like logic.
    在文件中极速搜索特定字符串（类似 grep）。
    """
    full_path = os.path.abspath(os.path.join(SECURE_ROOT, relative_path))
    if not full_path.startswith(os.path.abspath(SECURE_ROOT)):
        raise ValueError("Access Denied")

    # 使用 Python 实现轻量级搜索，避免大文件内存溢出 (Memory Safe)
    results = []
    with open(full_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if query.lower() in line.lower():
                results.append(f"L{i+1}: {line.strip()}")
            if len(results) > 20: # 仅返回前20个匹配项，防止回显爆炸
                results.append("... (Too many matches, please refine your query)")
                break
    
    return "\n".join(results) if results else "No matches found."

@mcp.tool()
async def data_summary_stats(relative_path: str) -> str:
    """
    Generate summary statistics for a data file (columns types, null counts, basic stats).
    生成数据文件的概要统计（列类型、空值统计、基础统计量）。
    """
    full_path = os.path.abspath(os.path.join(SECURE_ROOT, relative_path))
    if not full_path.startswith(os.path.abspath(SECURE_ROOT)):
        raise ValueError("Access Denied")

    import pandas as pd
    import io
    
    ext = os.path.splitext(relative_path)[1].lower()
    try:
        if ext == ".parquet":
            df = pd.read_parquet(full_path)
        else:
            df = pd.read_csv(full_path)
            
        # 1. Basic Info (Types and Nulls)
        buffer = io.StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()
        
        # 2. Descriptive Stats
        stats_md = df.describe(include='all').to_markdown()
        
        return f"### 数据概要 (Info):\n{info_str}\n\n### 描述性统计 (Statistics):\n{stats_md}"
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

if __name__ == "__main__":
    mcp.run()
