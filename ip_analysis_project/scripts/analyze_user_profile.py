"""
用户画像分析脚本
分析创作者和评论者的用户画像
"""

import os
import sys
import json
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


class UserProfileAnalyzer:
    """用户画像分析器"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.ips = ["明日方舟", "故宫", "恋与制作人"]
        self.results = {}

    def load_notes(self, ip_name: str) -> list:
        """加载笔记数据"""
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

        logger.info(f"加载 {ip_name} 笔记: {len(notes)} 条")
        return notes

    def load_comments(self, ip_name: str) -> list:
        """加载评论数据"""
        file_path = os.path.join(self.data_dir, f"{ip_name}_comments.jsonl")

        if not os.path.exists(file_path):
            logger.warning(f"评论文件不存在: {file_path}")
            return []

        comments = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    comments.append(data)
                except json.JSONDecodeError:
                    continue

        logger.info(f"加载 {ip_name} 评论: {len(comments)} 条")
        return comments

    def analyze_creator_profile(self, notes: list, ip_name: str) -> dict:
        """分析创作者画像"""
        # 按用户聚合
        users = defaultdict(
            lambda: {
                "nickname": "",
                "note_count": 0,
                "total_likes": 0,
                "total_collects": 0,
                "total_comments": 0,
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
            users[uid]["note_count"] += 1
            users[uid]["total_likes"] += int(interact.get("liked_count", 0) or 0)
            users[uid]["total_collects"] += int(interact.get("collected_count", 0) or 0)
            users[uid]["total_comments"] += int(interact.get("comment_count", 0) or 0)
            users[uid]["notes"].append(
                {
                    "title": card.get("display_title", ""),
                    "type": card.get("type", ""),
                    "likes": int(interact.get("liked_count", 0) or 0),
                }
            )

        # 计算影响力得分
        for uid, data in users.items():
            # 影响力 = 总互动 / 发布数量
            total_interact = (
                data["total_likes"]
                + data["total_collects"] * 2
                + data["total_comments"] * 3
            )
            data["influence_score"] = total_interact / max(data["note_count"], 1)
            data["user_id"] = uid

        # 排序
        sorted_users = sorted(
            users.values(), key=lambda x: x["influence_score"], reverse=True
        )

        return {
            "total_creators": len(users),
            "top_creators": sorted_users[:20],
            "all_creators": users,
        }

    def analyze_commenter_profile(self, comments: list, ip_name: str) -> dict:
        """分析评论者画像"""
        commenters = defaultdict(
            lambda: {"nickname": "", "comment_count": 0, "notes_commented": set()}
        )

        for comment in comments:
            note_id = comment.get("note_id", "")
            user_info = comment.get("user_info", {})

            uid = user_info.get("user_id")
            if not uid:
                continue

            commenters[uid]["nickname"] = user_info.get("nickname", "")
            commenters[uid]["comment_count"] += 1
            commenters[uid]["notes_commented"].add(note_id)

        # 转换set为list
        for uid, data in commenters.items():
            data["notes_commented"] = list(data["notes_commented"])
            data["unique_notes"] = len(data["notes_commented"])

        sorted_commenters = sorted(
            commenters.values(), key=lambda x: x["comment_count"], reverse=True
        )

        return {
            "total_commenters": len(commenters),
            "top_commenters": sorted_commenters[:20],
            "all_commenters": commenters,
        }

    def analyze_content_preference(self, notes: list, ip_name: str) -> dict:
        """分析内容偏好"""
        stats = {
            "type_preference": {"normal": 0, "video": 0},
            "content_themes": defaultdict(int),
            "publish_time_dist": defaultdict(int),
        }

        for note in notes:
            card = note.get("note_card", {})

            # 内容类型
            note_type = card.get("type", "normal")
            stats["type_preference"][note_type] += 1

            # 提取主题关键词（从标题）
            title = card.get("display_title", "")
            if title:
                # 简单提取关键词（实际可用jieba分词）
                stats["content_themes"][title[:10]] += 1

            # 发布时间分布
            corner_info = card.get("corner_tag_info", [])
            for tag in corner_info:
                if tag.get("type") == "publish_time":
                    stats["publish_time_dist"][tag.get("text", "")[:7]] += 1

        return stats

    def analyze_user_engagement(
        self, notes: list, comments: list, ip_name: str
    ) -> dict:
        """分析用户参与度"""
        # 创作者参与度
        creator_engagement = {
            "active_creators": 0,
            "high_output_creators": 0,  # 发布>=3篇
            "avg_notes_per_creator": 0,
        }

        users = defaultdict(int)
        for note in notes:
            user = note.get("note_card", {}).get("user", {})
            uid = user.get("user_id")
            if uid:
                users[uid] += 1

        total_notes = sum(users.values())
        creator_engagement["active_creators"] = len(users)
        creator_engagement["high_output_creators"] = sum(
            1 for v in users.values() if v >= 3
        )
        creator_engagement["avg_notes_per_creator"] = total_notes / max(len(users), 1)

        # 评论者参与度
        commenter_engagement = {
            "unique_commenters": 0,
            "high_engagement_commenters": 0,  # 评论>=3次
            "avg_comments_per_commenter": 0,
        }

        commenters = defaultdict(int)
        for comment in comments:
            user_info = comment.get("user_info", {})
            uid = user_info.get("user_id")
            if uid:
                commenters[uid] += 1

        total_comments = sum(commenters.values())
        commenter_engagement["unique_commenters"] = len(commenters)
        commenter_engagement["high_engagement_commenters"] = sum(
            1 for v in commenters.values() if v >= 3
        )
        commenter_engagement["avg_comments_per_commenter"] = total_comments / max(
            len(commenters), 1
        )

        return {
            "creators": creator_engagement,
            "commenters": commenter_engagement,
            "engagement_ratio": total_comments / max(total_notes, 1),
        }

    def generate_report(self, results: dict) -> str:
        """生成用户画像报告"""
        lines = []
        lines.append("# 👤 用户画像分析报告\n")

        for ip, data in results.items():
            lines.append(f"## 🎮 {ip}\n")

            # 创作者画像
            lines.append("### 创作者画像")
            creator = data["creators"]
            lines.append(f"- 独立创作者: {creator['total_creators']} 人")
            lines.append(f"- 高产创作者 (>=3篇): {creator['high_output_creators']} 人")
            lines.append(f"- 人均发布: {creator['avg_notes_per_creator']:.1f} 篇")
            lines.append("")

            lines.append("#### TOP 10 影响力创作者")
            lines.append("| 排名 | 昵称 | 发布数 | 总点赞 | 总收藏 | 影响力得分 |")
            lines.append("|------|------|--------|--------|--------|-----------|")

            for i, c in enumerate(data["top_creators"][:10], 1):
                lines.append(
                    f"| {i} | {c['nickname']} | {c['note_count']} | "
                    f"{c['total_likes']} | {c['total_collects']} | "
                    f"{c['influence_score']:.1f} |"
                )
            lines.append("")

            # 评论者画像
            commenter = data["commenters"]
            lines.append("### 评论者画像")
            lines.append(f"- 独立评论者: {commenter['total_commenters']} 人")
            lines.append(
                f"- 高频评论者 (>=3次): {commenter['high_engagement_commenters']} 人"
            )
            lines.append(
                f"- 人均评论: {commenter['avg_comments_per_commenter']:.1f} 次"
            )
            lines.append("")

            lines.append("#### TOP 10 活跃评论者")
            lines.append("| 排名 | 昵称 | 评论数 |")
            lines.append("|------|------|--------|")

            for i, c in enumerate(data["top_commenters"][:10], 1):
                lines.append(f"| {i} | {c['nickname']} | {c['comment_count']} |")
            lines.append("")

            # 内容偏好
            pref = data["content_preference"]
            lines.append("### 内容偏好")
            lines.append(f"- 图文笔记: {pref['type_preference'].get('normal', 0)} 篇")
            lines.append(f"- 视频笔记: {pref['type_preference'].get('video', 0)} 篇")
            lines.append(
                f"- 视频占比: {pref['type_preference'].get('video', 0) / max(pref['type_preference'].get('normal', 0) + pref['type_preference'].get('video', 0), 1) * 100:.1f}%"
            )
            lines.append("")

            # 参与度
            engage = data["engagement"]
            lines.append("### 参与度分析")
            lines.append(f"- 创作者活跃数: {engage['creators']['active_creators']}")
            lines.append(
                f"- 评论互动比: {engage['engagement_ratio']:.2f} (评论数/笔记数)"
            )
            lines.append("")

            lines.append("---\n")

        return "\n".join(lines)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "datas")
    output_dir = os.path.join(project_dir, "output")

    analyzer = UserProfileAnalyzer(data_dir)
    results = {}

    for ip in analyzer.ips:
        logger.info(f"分析 {ip} 用户画像...")
        notes = analyzer.load_notes(ip)
        comments = analyzer.load_comments(ip)

        results[ip] = {
            "creators": analyzer.analyze_creator_profile(notes, ip),
            "commenters": analyzer.analyze_commenter_profile(comments, ip),
            "content_preference": analyzer.analyze_content_preference(notes, ip),
            "engagement": analyzer.analyze_user_engagement(notes, comments, ip),
        }

    # 保存结果
    os.makedirs(output_dir, exist_ok=True)

    # JSON
    json_file = os.path.join(output_dir, "user_profile_analysis.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Markdown报告
    report = analyzer.generate_report(results)
    md_file = os.path.join(output_dir, "user_profile_report.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info("✅ 用户画像分析完成!")
    print(f"\n📄 报告已保存: {md_file}")


if __name__ == "__main__":
    main()
