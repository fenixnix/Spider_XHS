# XHS_IP_Analysis - 收藏卡片IP数据分析项目

## 项目概述

基于小红书平台数据分析，为**收藏卡片**（美术收藏品，非游戏属性）开发提供市场洞察。

## 分析IP

| IP | 类型 | 目标用户 | 收藏卡片定位 |
|----|-----|---------|------------|
| 明日方舟 | 二次元塔防游戏 | 核心游戏玩家 | 高品质角色插画卡 |
| 故宫 | 国风文化IP | 文化爱好者 | 国潮艺术收藏卡 |
| 恋与制作人 | 女性向恋爱游戏 | 女性玩家 | 情感收藏卡 |

## 项目结构

```
Spider_XHS/
└── ip_analysis_project/
    ├── datas/                    # 原始数据（JSONL格式）
    │   ├── 明日方舟.jsonl
    │   ├── 明日方舟_comments.jsonl
    │   ├── 故宫.jsonl
    │   ├── 故宫_comments.jsonl
    │   ├── 恋与制作人.jsonl
    │   └── 恋与制作人_comments.jsonl
    ├── scripts/                  # 数据爬取脚本
    │   ├── fetch_ip_data.py      # IP数据爬取（通用）
    │   ├── analyze_ip_heat.py    # IP热度分析
    │   ├── analyze_user_profile.py # 用户画像分析
    │   ├── analyze_creator_ranking.py # 创作者排行
    │   └── generate_report.py    # 报告生成
    ├── docs/                     # 文档
    │   ├── analysis_report.md    # 分析报告
    │   └── ip_insights.md        # IP洞察
    ├── requirements.txt          # 依赖
    └── config.py                  # 配置文件
```

## 分析维度

### 1. IP热度分析
- 笔记发布量趋势
- 互动数据分布（点赞/收藏/评论）
- 内容类型占比（图文vs视频）
- 热门话题/关键词

### 2. 用户画像分析
- 创作者活跃度分布
- 用户影响力层级
- 内容偏好分析
- 地域/时间分布

### 3. 创作者排行
- TOP影响力创作者
- 高产创作者
- 潜力创作者

## 快速开始

```bash
# 1. 进入项目目录
cd ip_analysis_project

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置Cookie
# 编辑 config.py 或使用环境变量
export XHS_COOKIE="your_cookie_here"

# 4. 爬取数据
python scripts/fetch_ip_data.py "明日方舟" --num 200
python scripts/fetch_ip_data.py "故宫" --num 200
python scripts/fetch_ip_data.py "恋与制作人" --num 200

# 5. 运行分析
python scripts/analyze_ip_heat.py
python scripts/analyze_user_profile.py
python scripts/analyze_creator_ranking.py
python scripts/generate_report.py
```

## 收藏卡片开发建议

基于数据分析，产出以下洞察：
- 哪类内容最适合制作收藏卡片
- 目标用户群体的审美偏好
- 最佳发布时机
- 差异化定位建议

## 版权声明

本项目仅供学习研究使用，数据来源于公开平台。
