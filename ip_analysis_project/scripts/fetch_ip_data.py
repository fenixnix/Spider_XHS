"""
IP数据爬取脚本 - 收藏卡片IP分析专用
基于Spider_XHS的fetch_by_subject.py
"""

import os
import sys
import json
import time
import random
import argparse
from datetime import datetime
from typing import Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from dotenv import load_dotenv
from apis.xhs_pc_apis import XHS_Apis

load_dotenv()


class IPDataCrawler:
    """IP数据爬取器"""

    def __init__(self):
        self.xhs_apis = XHS_Apis()
        self.cookies_str = os.getenv("COOKIES", "")

        # 随机延迟设置
        self.min_sleep = 2
        self.max_sleep = 5

    def _random_sleep(self):
        """随机延迟，避免被封"""
        sleep_time = random.uniform(self.min_sleep, self.max_sleep)
        logger.info(f"随机延迟 {sleep_time:.2f} 秒...")
        time.sleep(sleep_time)

    def fetch_notes(self, keyword: str, num: int = 200, sort: int = 4) -> list:
        """
        获取指定关键词的笔记

        Args:
            keyword: 搜索关键词（IP名称）
            num: 获取数量
            sort: 排序方式 0-综合, 1-最新, 2-最多点赞, 3-最多评论, 4-最多收藏

        Returns:
            笔记列表
        """
        if not self.cookies_str:
            raise ValueError("请先设置环境变量 COOKIES")

        logger.info(f"开始采集: {keyword}, 目标数量: {num}")

        note_list = []
        cursor_score = ""
        refresh_type = 1
        note_index = 0

        try:
            while len(note_list) < num:
                success, msg, res_json = self.xhs_apis.get_homefeed_recommend(
                    category=keyword,
                    cursor_score=cursor_score,
                    refresh_type=refresh_type,
                    note_index=note_index,
                    cookies_str=self.cookies_str,
                )

                if not success:
                    logger.error(f"API调用失败: {msg}")
                    break

                if "notes" not in res_json.get("data", {}):
                    logger.warning(f"没有找到笔记数据")
                    break

                notes = res_json["data"]["notes"]
                if not notes:
                    logger.warning("没有更多笔记了")
                    break

                note_list.extend(notes)
                logger.info(f"已采集 {len(note_list)} 条笔记")

                cursor_score = res_json["data"].get("cursor_score", "")
                refresh_type = 3  # 后续请求使用刷新类型3
                note_index += 20

                self._random_sleep()

        except Exception as e:
            logger.error(f"采集异常: {str(e)}")

        logger.info(f"采集完成: {keyword}, 共 {len(note_list)} 条笔记")
        return note_list[:num]

    def fetch_comments(self, note_id: str) -> list:
        """获取笔记评论"""
        try:
            success, msg, res_json = self.xhs_apis.get_note_comment(
                note_id=note_id, cookies_str=self.cookies_str
            )
            if success and res_json:
                return res_json.get("data", {}).get("comments", [])
        except Exception as e:
            logger.error(f"获取评论失败: {e}")
        return []

    def save_notes(self, notes: list, keyword: str, output_dir: str):
        """保存笔记数据到JSONL文件"""
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"{keyword}.jsonl")

        with open(output_file, "w", encoding="utf-8") as f:
            for note in notes:
                # 添加采集时间
                note["crawl_time"] = datetime.now().isoformat()
                note["hot_query"] = keyword
                f.write(json.dumps(note, ensure_ascii=False) + "\n")

        logger.info(f"笔记已保存: {output_file}")
        return output_file

    def save_comments(self, comments: list, keyword: str, output_dir: str):
        """保存评论数据"""
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"{keyword}_comments.jsonl")

        with open(output_file, "w", encoding="utf-8") as f:
            for comment in comments:
                f.write(json.dumps(comment, ensure_ascii=False) + "\n")

        logger.info(f"评论已保存: {output_file}")
        return output_file


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="IP数据爬取工具")
    parser.add_argument("keyword", type=str, help="搜索关键词（IP名称）")
    parser.add_argument("-n", "--num", type=int, default=200, help="采集数量")
    parser.add_argument("-o", "--output", type=str, default=None, help="输出目录")
    parser.add_argument(
        "-s",
        "--sort",
        type=int,
        default=4,
        help="排序方式: 0-综合, 1-最新, 2-最多点赞, 3-最多评论, 4-最多收藏",
    )

    args = parser.parse_args()

    # 确定输出目录
    if args.output:
        output_dir = args.output
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "..", "datas")

    # 创建爬虫并执行
    crawler = IPDataCrawler()

    # 采集笔记
    notes = crawler.fetch_notes(args.keyword, args.num, args.sort)

    if notes:
        # 保存笔记
        crawler.save_notes(notes, args.keyword, output_dir)

        logger.info(f"✅ {args.keyword} 数据采集完成!")
        logger.info(f"   笔记数量: {len(notes)}")
        logger.info(f"   输出目录: {output_dir}")
    else:
        logger.error(f"❌ {args.keyword} 数据采集失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
