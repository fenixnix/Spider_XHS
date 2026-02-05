# encoding: utf-8
"""
从 JSONL 文件中提取笔记作者ID列表

功能:
1. 解析小红书笔记JSONL文件
2. 提取所有笔记的作者ID
3. 去重并统计
4. 保存为文本文件

用法:
    python extract_authors.py <jsonl文件路径> [--output <输出文件>]

示例:
    python extract_authors.py datas/excel_datas/JOJO奇妙冒险.jsonl
    python extract_authors.py datas/excel_datas/JOJO奇妙冒险.jsonl -o authors_jojo.txt
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Set, Tuple, List, Dict


def parse_jsonl(file_path: str) -> Tuple[List[dict], int]:
    """
    解析 JSONL 文件

    Args:
        file_path: JSONL 文件路径

    Returns:
        Tuple[笔记列表, 解析失败数量]
    """
    notes = []
    failed_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                note = json.loads(line)
                notes.append(note)
            except json.JSONDecodeError as e:
                failed_count += 1
                if failed_count <= 3:  # 只打印前3个错误
                    print(f"⚠️ 第{line_num}行解析失败: {e}")

    return notes, failed_count


def extract_authors(notes: List[dict]) -> Tuple[Set[str], Dict[str, dict]]:
    """
    从笔记列表中提取作者信息

    Args:
        notes: 笔记列表

    Returns:
        Tuple[作者ID集合, 作者详情字典]
    """
    author_ids: Set[str] = set()
    author_details: Dict[str, dict] = {}

    for note in notes:
        try:
            # 获取 note_card
            note_card = note.get("note_card", {})
            if not note_card:
                continue

            # 获取用户信息
            user = note_card.get("user", {})
            if not user:
                continue

            user_id = user.get("user_id") or user.get("userId")
            if not user_id:
                continue

            # 添加到集合（自动去重）
            author_ids.add(user_id)

            # 保存详情（取第一个出现的详细信息）
            if user_id not in author_details:
                author_details[user_id] = {
                    "user_id": user_id,
                    "nickname": user.get("nickname", user.get("nick_name", "")),
                    "avatar": user.get("avatar", ""),
                }

        except Exception as e:
            print(f"⚠️ 解析作者信息失败: {e}")
            continue

    return author_ids, author_details


def print_author_summary(
    author_ids: Set[str], author_details: Dict[str, dict], file_name: str
):
    """
    打印作者统计摘要
    """
    print("\n" + "=" * 60)
    print("📊 作者统计摘要")
    print("=" * 60)
    print(f"📁 文件: {file_name}")
    print(f"📝 唯一作者数: {len(author_ids)}")
    print(f"📋 详情记录数: {len(author_details)}")
    print("=" * 60)


def save_author_ids(
    author_ids: Set[str], output_path: str, details: Dict[str, dict] = None
):
    """
    保存作者ID列表到文件

    Args:
        author_ids: 作者ID集合
        output_path: 输出文件路径
        details: 可选的作者详情字典
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# 小红书作者ID列表\n")
        f.write(f"# 生成时间: \n")
        f.write(f"# 总数量: {len(author_ids)}\n")
        f.write("#" + "=" * 50 + "\n\n")

        # 写入详情模式
        if details:
            for author_id in sorted(author_ids):
                info = details.get(author_id, {})
                nickname = info.get("nickname", "N/A")
                f.write(f"{author_id}\t{nickname}\n")
        else:
            # 只写入ID
            for author_id in sorted(author_ids):
                f.write(f"{author_id}\n")

    return output_path


def extract_authors_from_jsonl(
    jsonl_path: str, output_path: str = None, save_details: bool = True
) -> Tuple[bool, str, Set[str]]:
    """
    从JSONL文件提取作者ID的主函数

    Args:
        jsonl_path: JSONL文件路径
        output_path: 输出文件路径（可选）
        save_details: 是否保存详细信息（带昵称）

    Returns:
        Tuple[成功标志, 消息, 作者ID集合]
    """
    # 检查文件是否存在
    if not os.path.exists(jsonl_path):
        return False, f"文件不存在: {jsonl_path}", set()

    # 解析JSONL
    print(f"📖 正在解析: {jsonl_path}")
    notes, failed = parse_jsonl(jsonl_path)
    print(f"✅ 成功解析: {len(notes)} 条记录, 失败: {failed} 条")

    if not notes:
        return False, "没有有效的笔记数据", set()

    # 提取作者
    print("👤 正在提取作者信息...")
    author_ids, author_details = extract_authors(notes)

    # 打印摘要
    print_author_summary(author_ids, author_details, os.path.basename(jsonl_path))

    # 保存结果
    if output_path is None:
        # 默认输出到同目录
        base_name = os.path.splitext(jsonl_path)[0]
        output_path = f"{base_name}_authors.txt"

    save_author_ids(author_ids, output_path, author_details if save_details else None)
    print(f"💾 已保存到: {output_path}")

    return True, f"成功提取 {len(author_ids)} 个作者", author_ids


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="从JSONL文件提取小红书作者ID",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python extract_authors.py JOJO奇妙冒险.jsonl
  python extract_authors.py datas/excel_datas/JOJO奇妙冒险.jsonl -o authors.txt
  python extract_authors.py datas/excel_datas/*.jsonl -o all_authors.txt
        """,
    )

    parser.add_argument("jsonl_path", type=str, help="JSONL文件路径")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="输出文件路径（默认: <输入名>_authors.txt）",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="安静模式，只输出结果"
    )

    args = parser.parse_args()

    # 执行提取
    success, msg, author_ids = extract_authors_from_jsonl(
        jsonl_path=args.jsonl_path, output_path=args.output, save_details=True
    )

    if success:
        print(f"\n✅ {msg}")
        return 0
    else:
        print(f"\n❌ {msg}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
