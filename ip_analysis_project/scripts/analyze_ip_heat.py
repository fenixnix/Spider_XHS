"""
IP热度分析脚本
分析明日方舟、故宫、恋与制作人三个IP的小红书热度
"""

import os
import sys
import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jieba
from loguru import logger


class IPHeatAnalyzer:
    """IP热度分析器"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.ips = ["明日方舟", "故宫", "恋与制作人"]
        self.results = {}

    def load_data(self, ip_name: str) -> list:
        """加载指定IP的数据"""
        file_path = os.path.join(self.data_dir, f"{ip_name}.jsonl")

        if not os.path.exists(file_path):
            logger.warning(f"数据文件不存在: {file_path}")
            return []

        notes = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    notes.append(data)
                except json.JSONDecodeError:
                    continue

        logger.info(f"加载 {ip_name} 数据: {len(notes)} 条笔记")
        return notes

    def analyze_ip_heat(self, notes: list, ip_name: str) -> dict:
        """分析单个IP的热度"""
        if not notes:
            return {}

        stats = {
            "total_notes": len(notes),
            "type_distribution": {"normal": 0, "video": 0},
            "interact_stats": {
                "total_likes": 0,
                "total_collects": 0,
                "total_comments": 0,
                "total_shares": 0,
                "avg_likes": 0,
                "avg_collects": 0,
                "avg_comments": 0,
                "avg_shares": 0,
            },
            "top_notes": [],
            "keywords": defaultdict(int),
        }

        likes_list = []
        collects_list = []
        comments_list = []

        for note in notes:
            card = note.get("note_card", {})

            # 内容类型
            note_type = card.get("type", "normal")
            stats["type_distribution"][note_type] = (
                stats["type_distribution"].get(note_type, 0) + 1
            )

            # 互动数据
            interact = card.get("interact_info", {})
            likes = int(interact.get("liked_count", 0) or 0)
            collects = int(interact.get("collected_count", 0) or 0)
            comments = int(interact.get("comment_count", 0) or 0)
            shares = int(interact.get("shared_count", 0) or 0)

            likes_list.append(likes)
            collects_list.append(collects)
            comments_list.append(comments)

            stats["interact_stats"]["total_likes"] += likes
            stats["interact_stats"]["total_collects"] += collects
            stats["interact_stats"]["total_comments"] += comments
            stats["interact_stats"]["total_shares"] += shares

            # 提取标题关键词
            title = card.get("display_title", "")
            if title:
                words = jieba.cut(title)
                for word in words:
                    if len(word) > 1:
                        stats["keywords"][word] += 1

        # 计算平均值
        n = len(notes)
        if n > 0:
            stats["interact_stats"]["avg_likes"] = (
                stats["interact_stats"]["total_likes"] / n
            )
            stats["interact_stats"]["avg_collects"] = (
                stats["interact_stats"]["total_collects"] / n
            )
            stats["interact_stats"]["avg_comments"] = (
                stats["interact_stats"]["total_comments"] / n
            )
            stats["interact_stats"]["avg_shares"] = (
                stats["interact_stats"]["total_shares"] / n
            )

        # TOP 10 笔记（按点赞数）
        sorted_notes = sorted(
            notes,
            key=lambda x: int(
                x.get("note_card", {}).get("interact_info", {}).get("liked_count", 0)
                or 0
            ),
            reverse=True,
        )
        stats["top_notes"] = sorted_notes[:10]

        # 关键词排序
        stats["keywords"] = dict(
            sorted(stats["keywords"].items(), key=lambda x: x[1], reverse=True)[:50]
        )

        return stats

    def compare_ips(self):
        """对比分析所有IP"""
        logger.info("开始IP热度对比分析...")

        comparison = {"analyze_time": datetime.now().isoformat(), "ips": {}}

        for ip in self.ips:
            notes = self.load_data(ip)
            stats = self.analyze_ip_heat(notes, ip)
            comparison["ips"][ip] = stats

        return comparison

    def generate_report(self, comparison: dict) -> str:
        """生成分析报告"""
        report_lines = []
        report_lines.append("# 📊 IP热度分析报告\n")
        report_lines.append(f"分析时间: {comparison['analyze_time']}\n")
        report_lines.append("=" * 60 + "\n\n")

        for ip, stats in comparison["ips"].items():
            report_lines.append(f"## 🎮 {ip}\n")
            report_lines.append("### 基本统计")
            report_lines.append(f"- 笔记数量: {stats['total_notes']}")
            report_lines.append(
                f"- 图文笔记: {stats['type_distribution'].get('normal', 0)}"
            )
            report_lines.append(
                f"- 视频笔记: {stats['type_distribution'].get('video', 0)}"
            )
            report_lines.append("")

            report_lines.append("### 互动数据")
            interact = stats["interact_stats"]
            report_lines.append(f"- 总点赞: {interact['total_likes']:,}")
            report_lines.append(f"- 总收藏: {interact['total_collects']:,}")
            report_lines.append(f"- 总评论: {interact['total_comments']:,}")
            report_lines.append(f"- 总分享: {interact['total_shares']:,}")
            report_lines.append("")
            report_lines.append(f"- 平均点赞: {interact['avg_likes']:.1f}")
            report_lines.append(f"- 平均收藏: {interact['avg_collects']:.1f}")
            report_lines.append(f"- 平均评论: {interact['avg_comments']:.1f}")
            report_lines.append("")

            report_lines.append("### 高频关键词 TOP 20")
            keywords = list(stats["keywords"].items())[:20]
            for i, (word, count) in enumerate(keywords, 1):
                report_lines.append(f"{i:2}. {word} ({count})")
            report_lines.append("")
            report_lines.append("---\n")

        # 横向对比
        report_lines.append("## 📈 IP对比总结\n")
        report_lines.append("| IP | 笔记数 | 平均点赞 | 平均收藏 | 平均评论 |")
        report_lines.append("|----|--------|---------|---------|---------|")

        for ip, stats in comparison["ips"].items():
            interact = stats["interact_stats"]
            report_lines.append(
                f"| {ip} | {stats['total_notes']} | "
                f"{interact['avg_likes']:.1f} | {interact['avg_collects']:.1f} | "
                f"{interact['avg_comments']:.1f} |"
            )

        report_lines.append("")
        report_lines.append("## 💡 洞察建议\n")
        report_lines.append("（基于数据分析的洞察将在生成完整报告后补充）")

        return "\n".join(report_lines)

    def save_results(self, comparison: dict, output_dir: str):
        """保存分析结果"""
        os.makedirs(output_dir, exist_ok=True)

        # 保存JSON
        json_file = os.path.join(output_dir, "ip_heat_comparison.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(comparison, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON结果已保存: {json_file}")

        # 保存Markdown报告
        report = self.generate_report(comparison)
        md_file = os.path.join(output_dir, "ip_heat_report.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"报告已保存: {md_file}")


def main():
    """主函数"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "datas")
    output_dir = os.path.join(project_dir, "output")

    # 创建分析器
    analyzer = IPHeatAnalyzer(data_dir)

    # 执行分析
    comparison = analyzer.compare_ips()

    # 保存结果
    analyzer.save_results(comparison, output_dir)

    logger.info("✅ IP热度分析完成!")

    # 打印摘要
    print("\n" + "=" * 60)
    print("📊 IP热度分析摘要")
    print("=" * 60)

    for ip, stats in comparison["ips"].items():
        print(f"\n🎮 {ip}")
        print(f"   笔记数: {stats['total_notes']}")
        print(f"   平均点赞: {stats['interact_stats']['avg_likes']:.1f}")
        print(f"   平均收藏: {stats['interact_stats']['avg_collects']:.1f}")


if __name__ == "__main__":
    main()
