# encoding: utf-8
import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from typing import Optional

from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.common_util import init


def random_sleep(min_sec: float = 2.0, max_sec: float = 5.0) -> None:
    """
    随机休眠，模拟人类操作节奏
    :param min_sec: 最小秒数
    :param max_sec: 最大秒数
    """
    sleep_time = random.uniform(min_sec, max_sec)
    time.sleep(sleep_time)


def fetch_notes_by_subject(
    subtitle: str,
    quantity: int = 100,
    output: Optional[str] = None,
    sort: int = 0,
    note_type: int = 0,
    note_time: int = 0,
) -> tuple[bool, str, str]:
    """
    根据主题批量采集小红书笔记

    :param subtitle: 搜索关键词
    :param quantity: 采集数量（默认100）
    :param output: 输出文件名
    :param sort: 排序方式 0-综合, 1-最新, 2-最多点赞, 3-最多评论, 4-最多收藏
    :param note_type: 笔记类型 0-不限, 1-视频, 2-图文
    :param note_time: 发布时间 0-不限, 1-一天内, 2-一周内, 3-半年内
    :return: (success: bool, msg: str, file_path: str)
    """
    # 初始化
    cookies_str_result, base_path = init()
    if not cookies_str_result:
        logger.error("未找到有效的Cookie配置，请检查.env文件")
        return False, "Cookie未配置", ""
    cookies_str = cookies_str_result
    xhs_apis = XHS_Apis()

    # 设置输出文件
    safe_name = re.sub(r'[\\/:*?"<>|]', "_", subtitle)
    if not output:
        output = f"{safe_name}.jsonl"
    file_path = os.path.abspath(os.path.join(base_path["excel"], output))

    # 评论文件
    comments_file_path = os.path.abspath(
        os.path.join(base_path["excel"], f"{safe_name}_comments.jsonl")
    )

    page = 1
    total_count = 0

    logger.info(f"开始采集: {subtitle}, 目标数量: {quantity}, 输出: {file_path}")

    try:
        while total_count < quantity:
            # 请求前随机休眠
            random_sleep(2.0, 5.0)

            success, msg, res_json = xhs_apis.search_note(
                query=subtitle,
                cookies_str=cookies_str,
                page=page,
                sort_type_choice=sort,
                note_type=note_type,
                note_time=note_time,
            )

            if not success:
                logger.warning(f"第 {page} 页失败: {msg}")
                # 失败后等待更长时间
                random_sleep(10.0, 20.0)
                continue

            # 解析返回数据
            notes = []
            if res_json and "data" in res_json and "items" in res_json["data"]:
                notes = res_json["data"]["items"]

            if not notes:
                logger.info(f"第 {page} 页无数据，停止采集")
                break

            # 实时保存到 JSONL
            for note in notes:
                # 添加采集时间戳
                note["crawl_time"] = datetime.now().isoformat()

                # 保存笔记
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(note, ensure_ascii=False) + "\n")
                total_count += 1

                # 获取并保存评论
                note_id = note.get("id") or note.get("note_id")
                xsec_token = note.get("xsec_token", "")
                if note_id:
                    random_sleep(1.0, 2.0)  # 获取评论前短暂休眠
                    try:
                        # 直接调用获取评论API
                        success_c, msg_c, out_comments = (
                            xhs_apis.get_note_all_out_comment(
                                note_id, xsec_token, cookies_str, {}
                            )
                        )
                        if success_c and out_comments:
                            # 获取二级评论
                            all_comments = []
                            for comment in out_comments:
                                all_comments.append(comment)
                                # 获取二级评论
                                if comment.get("sub_comment_has_more"):
                                    success_sub, msg_sub, sub_comments = (
                                        xhs_apis.get_note_all_inner_comment(
                                            comment, xsec_token, cookies_str, {}
                                        )
                                    )
                                    if success_sub and sub_comments:
                                        all_comments.extend(sub_comments)

                            # 保存评论，格式: {"note_id": <ID>, "comment": <数据>}
                            comment_record = {
                                "note_id": note_id,
                                "crawl_time": datetime.now().isoformat(),
                                "comment": all_comments,
                            }
                            with open(comments_file_path, "a", encoding="utf-8") as f:
                                f.write(
                                    json.dumps(comment_record, ensure_ascii=False)
                                    + "\n"
                                )
                            logger.info(
                                f"📝 笔记 {note_id}: 获取 {len(all_comments)} 条评论"
                            )
                        elif not success_c:
                            logger.debug(f"笔记 {note_id}: 获取评论失败 ({msg_c})")
                    except Exception as e:
                        logger.debug(f"笔记 {note_id} 获取评论异常: {e}")

                if total_count >= quantity:
                    break

            logger.info(f"第 {page} 页完成，累计 {total_count} 条")
            page += 1

            # 翻页后增加间隔
            random_sleep(3.0, 8.0)

    except Exception as e:
        logger.error(f"采集异常: {e}")
        return False, str(e), file_path

    logger.info(f"采集完成: {subtitle}, 共 {total_count} 条, 文件: {file_path}")
    return True, f"成功采集 {total_count} 条笔记", file_path


def main() -> None:
    """主入口"""
    parser = argparse.ArgumentParser(
        description="小红书笔记批量采集工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python fetch_by_subject.py "JOJO奇妙冒险"
  python fetch_by_subject.py "美妆" -n 200
  python fetch_by_subject.py "穿搭" -o "chuan_da.jsonl" --sort 1
        """,
    )

    # 核心参数
    parser.add_argument("subtitle", type=str, help="搜索关键词")
    parser.add_argument(
        "--quantity", "-n", type=int, default=100, help="采集数量（默认100）"
    )
    parser.add_argument("--output", "-o", type=str, default=None, help="输出文件名")

    # 可选筛选参数
    parser.add_argument(
        "--sort",
        type=int,
        default=0,
        choices=[0, 1, 2, 3, 4],
        help="排序方式: 0-综合排序, 1-最新, 2-最多点赞, 3-最多评论, 4-最多收藏",
    )
    parser.add_argument(
        "--type",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="笔记类型: 0-不限, 1-视频笔记, 2-普通笔记",
    )
    parser.add_argument(
        "--time",
        type=int,
        default=0,
        choices=[0, 1, 2, 3],
        help="发布时间: 0-不限, 1-一天内, 2-一周内, 3-半年内",
    )

    args = parser.parse_args()

    success, msg, file_path = fetch_notes_by_subject(
        subtitle=args.subtitle,
        quantity=args.quantity,
        output=args.output,
        sort=args.sort,
        note_type=args.type,
        note_time=args.time,
    )

    if success:
        print(f"\n✅ {msg}")
        print(f"📁 文件: {file_path}")
    else:
        print(f"\n❌ {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
