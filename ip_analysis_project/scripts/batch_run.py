"""
批量采集脚本 - 一键采集3个IP的数据
"""

import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from dotenv import load_dotenv

load_dotenv()


def batch_crawl(ips: list, num: int = 200, output_dir: str = None):
    """批量采集IP数据"""
    from scripts.fetch_ip_data import IPDataCrawler

    crawler = IPDataCrawler()
    results = {}

    for ip in ips:
        logger.info(f"\n{'=' * 50}")
        logger.info(f"开始采集: {ip}")
        logger.info(f"{'=' * 50}")

        try:
            notes = crawler.fetch_notes(ip, num)

            if notes:
                crawler.save_notes(notes, ip, output_dir)
                results[ip] = {"success": True, "count": len(notes)}
            else:
                results[ip] = {"success": False, "count": 0}

        except Exception as e:
            logger.error(f"采集 {ip} 失败: {e}")
            results[ip] = {"success": False, "error": str(e)}

        # 间隔避免封禁
        time.sleep(5)

    return results


def run_all_analysis():
    """运行所有分析"""
    logger.info("\n" + "=" * 60)
    logger.info("开始执行数据分析...")
    logger.info("=" * 60)

    # 1. IP热度分析
    logger.info("\n📊 执行IP热度分析...")
    try:
        from scripts.analyze_ip_heat import IPHeatAnalyzer

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        data_dir = os.path.join(project_dir, "datas")
        output_dir = os.path.join(project_dir, "output")

        analyzer = IPHeatAnalyzer(data_dir)
        comparison = analyzer.compare_ips()
        analyzer.save_results(comparison, output_dir)
        logger.info("✅ IP热度分析完成")
    except Exception as e:
        logger.error(f"IP热度分析失败: {e}")

    # 2. 用户画像分析
    logger.info("\n👤 执行用户画像分析...")
    try:
        from scripts.analyze_user_profile import UserProfileAnalyzer

        analyzer = UserProfileAnalyzer(data_dir)
        results = {}

        for ip in ["明日方舟", "故宫", "恋与制作人"]:
            notes = analyzer.load_notes(ip)
            comments = analyzer.load_comments(ip)

            results[ip] = {
                "creators": analyzer.analyze_creator_profile(notes, ip),
                "commenters": analyzer.analyze_commenter_profile(comments, ip),
                "content_preference": analyzer.analyze_content_preference(notes, ip),
                "engagement": analyzer.analyze_user_engagement(notes, comments, ip),
            }

        # 保存
        import json

        os.makedirs(output_dir, exist_ok=True)
        json_file = os.path.join(output_dir, "user_profile_analysis.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        report = analyzer.generate_report(results)
        md_file = os.path.join(output_dir, "user_profile_report.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info("✅ 用户画像分析完成")
    except Exception as e:
        logger.error(f"用户画像分析失败: {e}")

    # 3. 创作者排行
    logger.info("\n🏆 执行创作者排行分析...")
    try:
        from scripts.analyze_creator_ranking import CreatorRankingAnalyzer

        analyzer = CreatorRankingAnalyzer(data_dir)
        all_creators_by_ip = {}
        all_creators_flat = []

        for ip in ["明日方舟", "故宫", "恋与制作人"]:
            notes = analyzer.load_notes(ip)
            if notes:
                creators = analyzer.calculate_creator_metrics(notes, ip)
                classified = analyzer.classify_creators(creators)
                all_creators_by_ip[ip] = classified
                all_creators_flat.extend(creators)

        import json

        json_file = os.path.join(output_dir, "creator_ranking.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(all_creators_flat, f, ensure_ascii=False, indent=2)

        logger.info("✅ 创作者排行分析完成")
    except Exception as e:
        logger.error(f"创作者排行分析失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="收藏卡片IP数据分析 - 批量工具")
    parser.add_argument("--crawl", action="store_true", help="执行数据采集")
    parser.add_argument("--analyze", action="store_true", help="执行数据分析")
    parser.add_argument("--all", action="store_true", help="执行全部（采集+分析）")
    parser.add_argument("-n", "--num", type=int, default=200, help="每个IP采集数量")

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(project_dir, "datas")

    ips = ["明日方舟", "故宫", "恋与制作人"]

    if args.all or args.crawl:
        logger.info("🚀 开始批量采集...")
        results = batch_crawl(ips, args.num, data_dir)

        print("\n" + "=" * 50)
        print("📊 采集结果汇总")
        print("=" * 50)
        for ip, result in results.items():
            status = "✅ 成功" if result["success"] else "❌ 失败"
            print(f"{ip}: {status} ({result.get('count', 0)} 条)")

    if args.all or args.analyze:
        run_all_analysis()

    if not any([args.crawl, args.analyze, args.all]):
        print("使用说明:")
        print("  --crawl     : 仅采集数据")
        print("  --analyze   : 仅运行分析")
        print("  --all       : 采集+分析（默认）")
        print("  -n NUM      : 每个IP采集数量（默认200）")
        print("\n示例:")
        print("  python batch_run.py --all -n 200")


if __name__ == "__main__":
    main()
