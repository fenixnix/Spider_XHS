"""
创作者影响力排行脚本
"""

import os
import sys
import json
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


class CreatorRankingAnalyzer:
    """创作者排行分析器"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.ips = ["明日方舟", "故宫", "恋与制作人"]

    def load_notes(self, ip_name: str) -> list:
        file_path = os.path.join(self.data_dir, f"{ip_name}.jsonl")
        if not os.path.exists(file_path):
            return []

        notes = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    notes.append(data)
                except:
                    continue
        return notes

    def calculate_creator_metrics(self, notes: list, ip_name: str) -> list:
        """计算创作者各项指标"""
        users = defaultdict(
            lambda: {
                "nickname": "",
                "avatar": "",
                "note_count": 0,
                "total_likes": 0,
                "total_collects": 0,
                "total_comments": 0,
                "total_shares": 0,
                "notes": [],
            }
        )

        for note in notes:
            card = note.get("note_card", {})
            user = card.get("user", {})
            interact = card.get("interact_info", {})

            uid = user.get("user_id")
            if not uid:
                continue

            users[uid]["nickname"] = user.get("nickname", "")
            users[uid]["avatar"] = user.get("avatar", "")
            users[uid]["note_count"] += 1
            users[uid]["total_likes"] += int(interact.get("liked_count", 0) or 0)
            users[uid]["total_collects"] += int(interact.get("collected_count", 0) or 0)
            users[uid]["total_comments"] += int(interact.get("comment_count", 0) or 0)
            users[uid]["total_shares"] += int(interact.get("shared_count", 0) or 0)

        # 计算综合得分
        results = []
        for uid, data in users.items():
            # 综合影响力得分 = 点赞*1 + 收藏*3 + 评论*5 + 分享*3
            raw_score = (
                data["total_likes"] * 1
                + data["total_collects"] * 3
                + data["total_comments"] * 5
                + data["total_shares"] * 3
            )

            # 人均影响力
            avg_score = raw_score / max(data["note_count"], 1)

            results.append(
                {
                    "user_id": uid,
                    "nickname": data["nickname"],
                    "avatar": data["avatar"],
                    "ip": ip_name,
                    "note_count": data["note_count"],
                    "total_likes": data["total_likes"],
                    "total_collects": data["total_collects"],
                    "total_comments": data["total_comments"],
                    "total_shares": data["total_shares"],
                    "raw_score": raw_score,
                    "avg_score": avg_score,
                    "raw_rank": 0,
                    "avg_rank": 0,
                }
            )

        # 排序
        results.sort(key=lambda x: x["raw_score"], reverse=True)
        for i, r in enumerate(results):
            r["raw_rank"] = i + 1

        results.sort(key=lambda x: x["avg_score"], reverse=True)
        for i, r in enumerate(results):
            r["avg_rank"] = i + 1

        return results

    def classify_creators(self, creators: list) -> dict:
        """创作者分类"""
        classified = {
            "top_kols": [],  # 头部KOL (score > 10000)
            "mid_influencers": [],  # 中腰部 (1000 < score <= 10000)
            "nano_influencers": [],  # 尾部 (100 < score <= 1000)
            "regular_creators": [],  # 普通创作者 (score <= 100)
            "high_output": [],  # 高产创作者 (>=5篇)
        }

        for c in creators:
            if c["raw_score"] > 10000:
                classified["top_kols"].append(c)
            elif c["raw_score"] > 1000:
                classified["mid_influencers"].append(c)
            elif c["raw_score"] > 100:
                classified["nano_influencers"].append(c)
            else:
                classified["regular_creators"].append(c)

            if c["note_count"] >= 5:
                classified["high_output"].append(c)

        return classified

    def generate_report(self, all_creators: dict, ip_name: str) -> str:
        """生成报告"""
        lines = []
        lines.append(f"## 🏆 {ip_name} 创作者排行\n")

        # 分类统计
        lines.append("### 创作者分层\n")
        lines.append(f"| 层级 | 人数 | 占比 |")
        lines.append(f"|------|------|------|")

        total = sum(len(v) for v in all_creators.values())
        for name, creators in all_creators.items():
            pct = creators and f"{len(creators) / total * 100:.1f}%" or "0%"
            label = name.replace("_", " ").title()
            lines.append(f"| {label} | {len(creators)} | {pct} |")
        lines.append("")

        # TOP 10 综合影响力
        sorted_creators = sorted(
            [c for creator_list in all_creators.values() for c in creator_list],
            key=lambda x: x["raw_score"],
            reverse=True,
        )

        lines.append("### TOP 10 综合影响力创作者\n")
        lines.append("| 排名 | 昵称 | 发布数 | 点赞 | 收藏 | 评论 | 得分 |")
        lines.append("|------|------|--------|------|------|------|------|")

        for i, c in enumerate(sorted_creators[:10], 1):
            lines.append(
                f"| {i} | {c['nickname']} | {c['note_count']} | "
                f"{c['total_likes']} | {c['total_collects']} | "
                f"{c['total_comments']} | {c['raw_score']} |"
            )
        lines.append("")

        # 高产创作者 TOP 10
        high_output = sorted(
            [c for creator_list in all_creators.values() for c in creator_list],
            key=lambda x: x["note_count"],
            reverse=True,
        )[:10]

        lines.append("### TOP 10 高产创作者\n")
        lines.append("| 排名 | 昵称 | 发布数 | 粉丝互动 |")
        lines.append("|------|------|--------|----------|")

        for i, c in enumerate(high_output, 1):
            lines.append(
                f"| {i} | {c['nickname']} | {c['note_count']} | {c['raw_score']} |"
            )
        lines.append("")

        return "\n".join(lines)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "datas")
    output_dir = os.path.join(project_dir, "output")

    analyzer = CreatorRankingAnalyzer(data_dir)

    all_creators_by_ip = {}
    all_creators_flat = []

    for ip in analyzer.ips:
        notes = analyzer.load_notes(ip)
        if notes:
            creators = analyzer.calculate_creator_metrics(notes, ip)
            classified = analyzer.classify_creators(creators)
            all_creators_by_ip[ip] = classified
            all_creators_flat.extend(creators)

    # 生成报告
    report_lines = ["# 🏆 创作者影响力排行总报告\n"]
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    report_lines.append("---\n")

    for ip, classified in all_creators_by_ip.items():
        report_lines.append(analyzer.generate_report(classified, ip))

    # 保存
    os.makedirs(output_dir, exist_ok=True)

    # 保存详细数据
    output_file = os.path.join(output_dir, "creator_ranking.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_creators_flat, f, ensure_ascii=False, indent=2)

    # 保存报告
    md_file = os.path.join(output_dir, "creator_ranking_report.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    logger.info("✅ 创作者排行分析完成!")
    print(f"\n📄 报告已保存: {md_file}")


if __name__ == "__main__":
    main()
