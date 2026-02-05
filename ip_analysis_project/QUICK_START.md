# 收藏卡片IP数据分析项目 - 快速指南

## 已完成的工作

### 1. 项目结构
```
Spider_XHS/ip_analysis_project/
├── README.md              # 项目说明
├── requirements.txt        # 依赖列表
├── config.py             # 配置文件
├── .env.example          # Cookie配置示例
├── scripts/              # 脚本目录
│   ├── fetch_ip_data.py       # 数据爬取
│   ├── analyze_ip_heat.py     # IP热度分析
│   ├── analyze_user_profile.py # 用户画像
│   ├── analyze_creator_ranking.py # 创作者排行
│   └── batch_run.py           # 批量执行
├── datas/                # 数据目录（待采集）
└── output/               # 输出目录
```

### 2. 分析脚本功能

| 脚本 | 功能 |
|-----|------|
| fetch_ip_data.py | 采集小红书笔记数据 |
| analyze_ip_heat.py | 热度对比分析 |
| analyze_user_profile.py | 用户画像分析 |
| analyze_creator_ranking.py | 创作者影响力排行 |
| batch_run.py | 一键采集+分析 |

---

## 下一步操作

### 步骤1：配置Cookie
```bash
cd ip_analysis_project
cp .env.example .env
# 编辑 .env，填入小红书Cookie
```

### 步骤2：安装依赖
```bash
pip install -r requirements.txt
```

### 步骤3：采集数据
```bash
# 一键采集3个IP
python scripts/batch_run.py --crawl -n 200

# 或单独采集
python scripts/fetch_ip_data.py "明日方舟" -n 200
python scripts/fetch_ip_data.py "故宫" -n 200
python scripts/fetch_ip_data.py "恋与制作人" -n 200
```

### 步骤4：运行分析
```bash
python scripts/batch_run.py --all -n 200
```

---

## 分析输出

| 报告 | 说明 |
|-----|------|
| ip_heat_report.md | IP热度对比 |
| user_profile_report.md | 用户画像 |
| creator_ranking_report.md | 创作者排行 |

---

## Cookie获取方法
1. 登录小红书网页版
2. F12打开开发者工具
3. Network标签
4. 点击任意请求
5. 复制Request Headers中的Cookie
