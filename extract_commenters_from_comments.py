# encoding: utf-8
"""
从评论数据文件中提取用户ID列表

功能:
1. 读取评论JSONL文件（包含一级和二级评论）
2. 提取所有评论的用户ID
3. 去重并统计
4. 保存为文本文件

用法:
    python extract_commenters_from_comments.py <评论文件路径> [--output <输出文件>]

示例:
    python extract_commenters_from_comments.py datas/excel_datas/JOJO奇妙冒险_comments.jsonl
    python extract_commenters_from_comments.py datas/excel_datas/*_comments.jsonl -o all_commenters.txt
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Set, Dict, List, Tuple


def parse_comments_jsonl(file_path: str) -> Tuple[List[dict], int]:
    """
    解析评论JSONL文件

    Args:
        file_path: JSONL文件路径

    Returns:
        Tuple[评论记录列表, 解析失败数量]
    """
    records = []
    failed_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError as e:
                failed_count += 1
                if failed_count <= 3:
                    print(f"⚠️ 第{line_num}行解析失败: {e}")

    return records, failed_count


def extract_commenter_ids(records: List[dict]) -> Tuple[Set[str], Dict[str, dict]]:
    """
    从评论记录中提取用户ID

    Args:
        records: 评论记录列表

    Returns:
        Tuple[用户ID集合, 用户详情字典]
    """
    commenter_ids: Set[str] = set()
    commenter_details: Dict[str, dict] = {}

    for record in records:
        try:
            comments = record.get("comment", [])
            if not comments:
                continue

            for comment in comments:
                # 一级评论用户
                user = comment.get("user_info", comment.get("user", {}))
                user_id = user.get("user_id") or user.get("id")
                if user_id:
                    commenter_ids.add(user_id)
                    if user_id not in commenter_details:
                        commenter_details[user_id] = {
                            "user_id": user_id,
                            "nickname": user.get("nickname", user.get("nick_name", "")),
                            "note_id": record.get("note_id", ""),
                        }

                # 二级评论用户
                sub_comments = comment.get("sub_comments", [])
                for sub_comment in sub_comments:
                    sub_user = sub_comment.get("user_info", sub_comment.get("user", {}))
                    sub_user_id = sub_user.get("user_id") or sub_user.get("id")
                    if sub_user_id:
                        commenter_ids.add(sub_user_id)
                        if sub_user_id not in commenter_details:
                            commenter_details[sub_user_id] = {
                                "user_id": sub_user_id,
                                "nickname": sub_user.get(
                                    "nickname", sub_user.get("nick_name", "")
                                ),
                                "note_id": record.get("note_id", ""),
                            }

                # 二级评论用户
                sub_comments = comment.get("sub_comments", [])
                for sub_comment in sub_comments:
                    sub_user = sub_comment.get("user", {})
                    sub_user_id = sub_user.get("user_id") or sub_user.get("id")
                    if sub_user_id:
                        commenter_ids.add(sub_user_id)
                        if sub_user_id not in commenter_details:
                            commenter_details[sub_user_id] = {
                                "user_id": sub_user_id,
                                "nickname": sub_user.get(
                                    "nickname", sub_user.get("nick_name", "")
                                ),
                                "note_id": record.get("note_id", ""),
                            }

        except Exception as e:
            print(f"⚠️ 解析评论记录失败: {e}")
            continue

    return commenter_ids, commenter_details


def print_summary(
    commenter_ids: Set[str],
    commenter_details: Dict[str, dict],
    file_name: str,
    records_count: int,
):
    """
    打印统计摘要
    """
    print("\n" + "=" * 60)
    print("📊 评论用户统计摘要")
    print("=" * 60)
    print(f"📁 文件: {file_name}")
    print(f"📝 评论记录数: {records_count}")
    print(f"👤 唯一用户数: {len(commenter_ids)}")
    print(f"📋 详情记录数: {len(commenter_details)}")
    print("=" * 60)


def save_commenter_ids(
    commenter_ids: Set[str], output_path: str, details: Dict[str, dict] = None
):
    """
    保存用户ID列表到文件

    Args:
        commenter_ids: 用户ID集合
        output_path: 输出文件路径
        details: 可选的用户详情字典
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# 小红书评论用户ID列表\n")
        f.write(f"# 生成时间: {datetime.now().isoformat()}\n")
        f.write(f"# 总数量: {len(commenter_ids)}\n")
        f.write("#" + "=" * 50 + "\n\n")

        if details:
            for user_id in sorted(commenter_ids):
                info = details.get(user_id, {})
                nickname = info.get("nickname", "N/A")
                f.write(f"{user_id}\t{nickname}\n")
        else:
            for user_id in sorted(commenter_ids):
                f.write(f"{user_id}\n")

    return output_path


def extract_commenters_from_file(
    comments_file_path: str, output_path: str = None, save_details: bool = True
) -> Tuple[bool, str, Set[str]]:
    """
    从评论文件提取用户ID的主函数

    Args:
        comments_file_path: 评论JSONL文件路径
        output_path: 输出文件路径（可选）
        save_details: 是否保存详细信息（带昵称）

    Returns:
        Tuple[成功标志, 消息, 用户ID集合]
    """
    # 检查文件
    if not os.path.exists(comments_file_path):
        return False, f"文件不存在: {comments_file_path}", set()

    # 解析文件
    print(f"📖 正在解析: {comments_file_path}")
    records, failed = parse_comments_jsonl(comments_file_path)
    print(f"✅ 成功解析: {len(records)} 条记录, 失败: {failed} 条")

    if not records:
        return False, "没有有效的评论数据", set()

    # 提取用户
    print("👤 正在提取用户信息...")
    commenter_ids, commenter_details = extract_commenter_ids(records)

    # 打印摘要
    print_summary(
        commenter_ids,
        commenter_details,
        os.path.basename(comments_file_path),
        len(records),
    )

    # 保存结果
    if output_path is None:
        base_name = os.path.splitext(comments_file_path)[0]
        output_path = f"{base_name}_commenters.txt"

    save_commenter_ids(
        commenter_ids, output_path, commenter_details if save_details else None
    )
    print(f"💾 已保存到: {output_path}")

    return True, f"成功提取 {len(commenter_ids)} 个用户", commenter_ids


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="从评论JSONL文件提取用户ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python extract_commenters_from_comments.py JOJO奇妙冒险_comments.jsonl
  python extract_commenters_from_comments.py datas/excel_datas/*_comments.jsonl -o commenters.txt
        """,
    )

    parser.add_argument(
        "comments_path", type=str, help="评论JSONL文件路径（支持通配符）"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="输出文件路径（默认: <输入名>_commenters.txt）",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="安静模式，只输出结果"
    )

    args = parser.parse_args()

    # 支持通配符
    import glob

    files = glob.glob(args.comments_path)

    if not files:
        return False, f"未找到匹配的文件: {args.comments_path}", set()

    all_commenters: Set[str] = set()
    total_records = 0

    for file_path in files:
        success, msg, commenters = extract_commenters_from_file(
            comments_file_path=file_path,
            output_path=args.output if len(files) == 1 else None,
            save_details=True,
        )
        if success:
            all_commenters.update(commenters)

    print(f"\n✅ 共提取 {len(all_commenters)} 个唯一用户")

    return 0


if __name__ == "__main__":
    sys.exit(main())
