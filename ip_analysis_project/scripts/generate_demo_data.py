"""
生成模拟测试数据 - 用于验证分析脚本
"""

import json
import random
from datetime import datetime, timedelta

# 模拟用户池
nicknames_明日方舟 = [
    "博士今天抽卡了吗",
    "罗德岛后勤部",
    "整合运动卧底",
    "洁哥粉丝一枚",
    "阿米娅世界第一",
    "煌大招真可怕",
    "能天使厨",
    "银灰是我的",
    "博士我们回家",
    "凯尔希医生",
    "斯卡蒂蓝色深海",
    "陈晖洁警司",
    "明日方舟玩家",
    "yj你坏事做尽",
    "源石虫爱好者",
    "朊病毒防治中心",
]

nicknames_故宫 = [
    "故宫摄影师",
    "紫禁城游客",
    "国潮爱好者",
    "传统文化守护者",
    "皇家配色",
    "红墙白雪",
    "六百年故宫",
    "御猫铲屎官",
    "故宫文创控",
    "历史爱好者",
    "古建筑摄影",
    "汉服在故宫",
    "故宫咖啡",
    "脊兽收集者",
    "明清历史迷",
    "故宫志愿者",
]

nicknames_恋与制作人 = [
    "恋与制作人玩家",
    "白起学长",
    "李泽言女人",
    "周棋洛的小太阳",
    "许墨的科学家",
    "狗叠还我老公",
    "乙女游戏玩家",
    "恋与抽卡玄学",
    "四个男人",
    "纸片人老公",
    "恋与通关记录",
    "头像是我老公",
    "狗叠鲨了你",
    "白起yyds",
    "李泽言的早餐",
    "周棋洛同款奶茶",
]

# 关键词池
keywords_明日方舟 = [
    "干员",
    "抽卡",
    "yj",
    "博士",
    "罗德岛",
    "源石",
    "凯尔希",
    "阿米娅",
    "银灰",
    "能天使",
    "煌",
    "斯卡蒂",
    "陈",
    "限定",
    "六星",
    "五星",
    "皮肤",
    "剧情",
    "剿灭",
    "肉鸽",
    "集成战略",
]

keywords_故宫 = [
    "故宫",
    "红墙",
    "琉璃瓦",
    "御猫",
    "文创",
    "雪景",
    "汉服",
    "拍照",
    "旅游",
    "攻略",
    "门票",
    "钟表馆",
    "珍宝馆",
    "角楼",
    "脊兽",
    "皇家",
    "清朝",
    "明朝",
    "御花园",
]

keywords_恋与制作人 = [
    "白起",
    "李泽言",
    "周棋洛",
    "许墨",
    "恋与制作人",
    "狗叠",
    "抽卡",
    "SSR",
    "约会",
    "剧情",
    "头像框",
    "限定",
    "周年庆",
    "电话",
    "短信",
    "乙女",
    "纸片人",
    "老公",
]


def generate_note(ip_name: str, idx: int) -> dict:
    """生成单条笔记"""
    nicknames = {
        "明日方舟": nicknames_明日方舟,
        "故宫": nicknames_故宫,
        "恋与制作人": nicknames_恋与制作人,
    }
    keywords = {
        "明日方舟": keywords_明日方舟,
        "故宫": keywords_故宫,
        "恋与制作人": keywords_恋与制作人,
    }

    nickname = random.choice(nicknames[ip_name])
    uid = f"{random.randint(0, 9):x}{random.randint(10000000, 99999999):x}{random.randint(0, 9):x}"

    # 互动数据（符合真实分布）
    if random.random() < 0.1:  # 10%爆款
        likes = random.randint(5000, 50000)
        collects = random.randint(500, 5000)
        comments = random.randint(100, 1000)
    elif random.random() < 0.3:  # 30%中等
        likes = random.randint(500, 5000)
        collects = random.randint(50, 500)
        comments = random.randint(10, 100)
    else:  # 60%普通
        likes = random.randint(10, 500)
        collects = random.randint(0, 50)
        comments = random.randint(0, 20)

    # 随机标题
    title_words = random.sample(keywords[ip_name], random.randint(2, 4))
    title = "".join(title_words)

    # 发布时间（最近90天）
    days_ago = random.randint(0, 90)
    publish_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    return {
        "id": f"{random.randint(0, 9):x}{idx:08x}{random.randint(0, 9):x}",
        "model_type": "note",
        "xsec_token": f"AB{random.randint(10, 99)}X{random.randint(1000, 9999)}",
        "crawl_time": datetime.now().isoformat(),
        "hot_query": ip_name,
        "note_card": {
            "type": random.choice(["normal", "normal", "normal", "video"]),
            "display_title": f"{nickname}: {title}",
            "cover": {
                "height": random.randint(1000, 3000),
                "width": random.randint(1000, 2000),
                "url_default": f"http://example.com/cover_{idx}.jpg",
                "url_pre": f"http://example.com/cover_{idx}_prv.jpg",
            },
            "image_list": [],
            "interact_info": {
                "liked": False,
                "liked_count": str(likes),
                "collected": False,
                "collected_count": str(collects),
                "comment_count": str(comments),
                "shared_count": str(random.randint(0, comments // 2)),
            },
            "user": {
                "user_id": uid,
                "nickname": nickname,
                "nick_name": nickname,
                "avatar": f"http://example.com/avatar_{uid}.jpg",
                "xsec_token": f"AB{random.randint(10, 99)}Y{random.randint(1000, 9999)}",
            },
            "corner_tag_info": [{"type": "publish_time", "text": publish_date}],
        },
    }


def generate_comments(note_id: str, ip_name: str, count: int) -> dict:
    """生成评论数据"""
    nicknames = {
        "明日方舟": nicknames_明日方舟,
        "故宫": nicknames_故宫,
        "恋与制作人": nicknames_恋与制作人,
    }

    comments_list = []
    for i in range(random.randint(1, min(count, 10))):
        nickname = random.choice(nicknames[ip_name])
        uid = f"{random.randint(0, 9):x}{random.randint(10000000, 99999999):x}{random.randint(0, 9):x}"

        comments_list.append(
            {
                "id": f"{random.randint(0, 9):x}{i:04x}{random.randint(0, 9):x}",
                "note_id": note_id,
                "content": f"这是{nickname}的评论内容#{i + 1}",
                "like_count": str(random.randint(0, 100)),
                "create_time": int(datetime.now().timestamp() * 1000),
                "ip_location": random.choice(
                    [
                        "北京",
                        "上海",
                        "广东",
                        "浙江",
                        "江苏",
                        "四川",
                        "湖北",
                        "山东",
                        "河南",
                        "河北",
                    ]
                ),
                "user_info": {
                    "user_id": uid,
                    "nickname": nickname,
                    "image": f"http://example.com/user_{uid}.jpg",
                    "ai_agent": False,
                    "xsec_token": f"AB{random.randint(10, 99)}Z{random.randint(1000, 9999)}",
                },
            }
        )

    return {
        "note_id": note_id,
        "crawl_time": datetime.now().isoformat(),
        "comment": comments_list,
    }


def main():
    """生成所有测试数据"""
    ips = ["明日方舟", "故宫", "恋与制作人"]

    base_dir = "datas"
    os.makedirs(base_dir, exist_ok=True)

    for ip in ips:
        # 生成笔记数据
        notes_file = os.path.join(base_dir, f"{ip}.jsonl")
        with open(notes_file, "w", encoding="utf-8") as f:
            for i in range(100):  # 每IP 100条
                note = generate_note(ip, i)
                f.write(json.dumps(note, ensure_ascii=False) + "\n")

        # 生成评论数据
        comments_file = os.path.join(base_dir, f"{ip}_comments.jsonl")
        with open(comments_file, "w", encoding="utf-8") as f:
            for i in range(50):  # 每IP 50条评论
                note_id = f"{random.randint(0, 9):x}{i:08x}{random.randint(0, 9):x}"
                comment = generate_comments(note_id, ip, 5)
                f.write(json.dumps(comment, ensure_ascii=False) + "\n")

        print(f"✅ 生成 {ip}: 100条笔记 + 50条评论")

    print("\n🎉 测试数据生成完成!")
    print("\n下一步:")
    print("  1. cd ip_analysis_project")
    print("  2. pip install -r requirements.txt")
    print("  3. python scripts/batch_run.py --analyze")


if __name__ == "__main__":
    import os

    main()
