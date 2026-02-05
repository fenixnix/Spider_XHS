# 小红书数据采集工具使用手册

本文档介绍小红书数据采集工具集的使用方法，适用于团队成员快速上手。

---

## 目录

- [1. 环境准备](#1-环境准备)
- [2. 采集笔记并获取评论](#2-采集笔记并获取评论)
- [3. 提取作者ID](#3-提取作者id)
- [4. 获取评论者ID](#4-获取评论者id)
- [5. 从评论提取用户列表](#5-从评论提取用户列表)
- [6. 链接生成工具](#6-链接生成工具)
- [7. 数据文件说明](#7-数据文件说明)

---

## 1. 环境准备

### 1.1 安装依赖

```bash
# Python 依赖
pip install -r requirements.txt

# Node.js 依赖（用于加密签名）
npm install
```

### 1.2 配置 Cookie

在项目根目录创建或编辑 `.env` 文件：

```
COOKIES=你的小红书Cookie字符串
```

**获取 Cookie 方法**：
1. 浏览器登录小红书
2. 按 F12 打开开发者工具
3. 切换到 Network（网络）标签
4. 刷新页面，点击任意请求
5. 在 Request Headers 中找到 Cookie，复制粘贴到 `.env`

---

## 2. 采集笔记并获取评论

### 2.1 命令

```bash
# 基础用法（采集100条，默认文件名）
python fetch_by_subject.py "美妆"

# 指定数量
python fetch_by_subject.py "穿搭" -n 200

# 指定输出文件名
python fetch_by_subject.py "美食" -o "meishi.jsonl"

# 带筛选条件
python fetch_by_subject.py "护肤" -n 500 --sort 2 --type 2 --time 1
```

### 2.2 参数说明

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| subtitle | - | 必填 | 搜索关键词 |
| quantity | -n | 100 | 采集数量 |
| output | -o | `{主题}.jsonl` | 输出文件名 |
| sort | - | 0 | 排序方式（0综合/1最新/2点赞/3评论/4收藏） |
| type | - | 0 | 类型（0不限/1视频/2图文） |
| time | - | 0 | 时间（0不限/1一天/2一周/3半年） |

### 2.3 输出文件

```
datas/excel_datas/
├── 美妆.jsonl              # 笔记数据
└── 美妆_comments.jsonl    # 评论数据
```

---

## 3. 提取作者ID

从已采集的笔记JSONL文件中提取所有笔记作者。

### 3.1 命令

```bash
# 从指定文件提取
python extract_authors.py datas/excel_datas/美妆.jsonl

# 指定输出文件
python extract_authors.py datas/excel_datas/美妆.jsonl -o authors.txt
```

### 3.2 输出格式

```
# 小红书作者ID列表
# 总数量: 70
#==================================================

584458606a6a69696e3b9472	控师地狱
59912e0a5e87e74b7ab8999c	爱在黑洞里
...
```

---

## 4. 获取评论者ID

根据笔记列表，调用API获取每条笔记的评论者ID。

### 4.1 命令

```bash
# 从笔记文件获取评论者
python get_commenters.py datas/excel_datas/美妆.jsonl

# 只处理前20条笔记
python get_commenters.py datas/excel_datas/美妆.jsonl -n 20

# 指定输出文件
python get_commenters.py datas/excel_datas/美妆.jsonl -o commenters_raw.txt
```

### 4.2 输出格式

```
# 小红书评论者ID列表
# 生成时间: 2026-02-05T11:31:45.982369
# 总数量: 11
#==================================================

640439f4000000002a0085a1	Vera看数据
6539d9e4000000000d006b3f	AI整活研究所
...
```

---

## 5. 从评论提取用户列表

从评论JSONL文件中提取所有评论用户ID（含一级和二级评论）。

### 5.1 命令

```bash
# 从评论文件提取用户
python extract_commenters_from_comments.py datas/excel_datas/美妆_comments.jsonl

# 批量处理多个文件
python extract_commenters_from_comments.py "datas/excel_datas/*_comments.jsonl"

# 指定输出文件
python extract_commenters_from_comments.py datas/excel_datas/美妆_comments.jsonl -o all_users.txt
```

### 5.2 输出格式

```
# 小红书评论用户ID列表
# 生成时间: 2026-02-05T11:36:35.114178
# 总数量: 5
#==================================================

# 格式: 用户ID	昵称	主页链接
#--------------------------------------------------

595206b750c4b41b00bcab4e	软喵心理	https://www.xiaohongshu.com/user/profile/595206b750c4b41b00bcab4e
5a94e6da4eacab3f4c3f9c58	一只崽tok	https://www.xiaohongshu.com/user/profile/5a94e6da4eacab3f4c3f9c58
```

---

## 6. 链接生成工具

在代码中导入使用，生成小红书链接。

### 6.1 导入方式

```python
from xhs_utils.xhs_link_util import note_url, user_url
```

### 6.2 函数说明

```python
# 生成笔记链接
note_url("68f71e060000000005011573")
# 返回: https://www.xiaohongshu.com/explore/68f71e060000000005011573

# 生成用户主页链接
user_url("584458606a6a69696e3b9472")
# 返回: https://www.xiaohongshu.com/user/profile/584458606a6a69696e3b9472

# 从URL提取笔记ID
extract_note_id("https://www.xiaohongshu.com/explore/68f71e06...")
# 返回: 68f71e060000000005011573

# 从URL提取用户ID
extract_user_id("https://www.xiaohongshu.com/user/profile/58445860...")
# 返回: 584458606a6a69696e3b9472
```

---

## 7. 数据文件说明

### 7.1 笔记数据 (xxx.jsonl)

每行一条JSON，结构如下：

```json
{
  "id": "68f71e060000000005011573",
  "model_type": "note",
  "xsec_token": "ABMew6WZDjUiGAWn...",
  "note_card": {
    "type": "normal",
    "display_title": "Jojo的奇妙合集",
    "cover": {...},
    "interact_info": {
      "liked_count": "18026",
      "collected_count": "3474",
      "comment_count": "265",
      "shared_count": "607"
    },
    "user": {
      "user_id": "584458606a6a69696e3b9472",
      "nickname": "控师地狱"
    }
  },
  "crawl_time": "2026-02-05T10:32:00.687238"
}
```

### 7.2 评论数据 (xxx_comments.jsonl)

每行一条评论记录：

```json
{
  "note_id": "6914afd2000000000703b43f",
  "crawl_time": "2026-02-05T11:26:30.123",
  "comment": [
    {
      "id": "6948aef10000000016025f0d",
      "content": "天王老子来了他也是88",
      "user_info": {
        "user_id": "640439f4000000002a0085a1",
        "nickname": "Vera看数据"
      }
    }
  ]
}
```

### 7.3 用户列表 (xxx_commenters.txt)

提取的用户ID列表，带主页链接：

```
# 小红书评论用户ID列表
# 总数量: 5
#==================================================

# 格式: 用户ID	昵称	主页链接
#--------------------------------------------------

640439f4000000002a0085a1	Vera看数据	https://www.xiaohongshu.com/user/profile/640439f4000000002a0085a1
```

---

## 8. 常见问题

### Q1: 采集失败，提示 Cookie 问题

确保 `.env` 文件中的 COOKIES 有效且未过期。重新登录小红书获取新的 Cookie。

### Q2: 部分笔记获取评论失败

可能原因：
- 笔记已删除或设为私密
- 笔记作者关闭了评论
- 网络问题

这些笔记会跳过处理，不影响其他笔记。

### Q3: 被限制访问

工具已内置随机休眠策略降低被封风险。如仍被限制：
1. 等待一段时间后再试
2. 更换 IP 地址
3. 更新 Cookie

---

## 9. 输出目录

所有数据文件默认保存在 `datas/excel_datas/` 目录：

```
Spider_XHS/
├── datas/excel_datas/
│   ├── 美妆.jsonl              # 笔记
│   ├── 美妆_comments.jsonl      # 评论
│   ├── 美妆_authors.txt         # 作者ID
│   └── 美妆_commenters.txt      # 评论用户ID
```

---

## 10. 快速开始示例

```bash
# 1. 采集"JOJO奇妙冒险"主题的100条笔记及评论
python fetch_by_subject.py "JOJO奇妙冒险"

# 2. 从笔记提取作者ID
python extract_authors.py datas/excel_datas/JOJO奇妙冒险.jsonl

# 3. 从评论数据提取所有评论用户
python extract_commenters_from_comments.py datas/excel_datas/JOJO奇妙冒险_comments.jsonl
```

---

## 11. 注意事项

1. **Cookie 安全**：不要将 `.env` 文件提交到代码仓库
2. **采集频率**：工具已内置随机休眠，不要修改休眠参数
3. **数据合规**：仅供学习研究使用，请遵守相关法律法规
4. **备份数据**：重要数据请额外备份
