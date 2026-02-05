"""
XHS IP Analysis Config
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """项目配置"""

    # 小红书Cookie（必需）
    XHS_COOKIE = os.getenv("XHS_COOKIE", "")

    # 数据目录
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datas")

    # 输出目录
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

    # 每个IP采集数量
    DEFAULT_CRAWL_NUM = 200

    # 请求间隔（秒）
    MIN_SLEEP = 2
    MAX_SLEEP = 5

    # IP列表
    IP_LIST = ["明日方舟", "故宫", "恋与制作人"]


if __name__ == "__main__":
    print(
        f"Cookie: {Config.XHS_COOKIE[:20]}..."
        if Config.XHS_COOKIE
        else "Cookie: Not set"
    )
    print(f"Data dir: {Config.DATA_DIR}")
