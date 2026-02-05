# 小红书笔记数据结构文档

## 1. 数据概览

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | ✅ | 笔记唯一ID |
| model_type | string | ✅ | 模型类型（固定为 "note"） |
| xsec_token | string | ✅ | 安全令牌 |
| crawl_time | string | ✅ | 采集时间（ISO格式） |
| hot_query | string | ❌ | 热门搜索词（部分记录有） |
| note_card | object | ✅ | 笔记详情对象 |

## 2. note_card 详细结构

### 2.1 一级字段

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 笔记类型：normal（图/文）、video（视频） |
| display_title | string | 笔记标题 |
| cover | object | 封面图片信息 |
| image_list | array | 图片列表（图集） |
| interact_info | object | 互动数据（点赞、收藏等） |
| user | object | 作者信息 |
| corner_tag_info | array | 角标信息（如发布时间） |

### 2.2 cover 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| width | int | 封面宽度 |
| height | int | 封面高度 |
| url_default | string | 默认封面URL |
| url_pre | string | 预览封面URL |

### 2.3 image_list 数组

每个元素包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| width | int | 图片宽度 |
| height | int | 图片高度 |
| info_list | array | 图片详情列表 |

**info_list 元素**：

| 字段 | 类型 | 说明 |
|------|------|------|
| image_scene | string | 场景：WB_DFT（默认）、WB_PRV（预览） |
| url | string | 图片URL |

### 2.4 interact_info 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| liked | boolean | 当前用户是否点赞 |
| liked_count | string | 点赞数 |
| collected | boolean | 当前用户是否收藏 |
| collected_count | string | 收藏数 |
| comment_count | string | 评论数 |
| shared_count | string | 分享数 |

### 2.5 user 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | string | 用户ID |
| nickname | string | 用户昵称 |
| nick_name | string | 用户昵称（备用） |
| avatar | string | 头像URL |
| xsec_token | string | 用户安全令牌 |

### 2.6 corner_tag_info 数组

每个元素：

| 字段 | 类型 | 说明 |
|------|------|------|
| type | string | 类型：publish_time（发布时间） |
| text | string | 时间文本，如 "2025-10-21" |

## 3. 数据分布统计

| 指标 | 数值 |
|------|------|
| 总记录数 | 100 |
| 完整笔记（note_card 完整） | 91 |
| 图/文笔记（normal） | 73 |
| 视频笔记（video） | 18 |
| 有 hot_query | 9 |

## 4. 示例数据

### 4.1 完整记录示例

```json
{
  "id": "68f71e060000000005011573",
  "model_type": "note",
  "xsec_token": "ABMew6WZDjUiGAWnfoS5Ky95w9J-s9EN1Oyz38s_Cbt-w=",
  "crawl_time": "2026-02-05T10:32:00.687238",
  "note_card": {
    "type": "normal",
    "display_title": "Jojo的奇妙合集",
    "cover": {
      "height": 2462,
      "width": 1080,
      "url_default": "http://sns-webpic-qc.xhscdn.com/...",
      "url_pre": "http://sns-webpic-qc.xhscdn.com/..."
    },
    "image_list": [
      {
        "height": 2462,
        "width": 1080,
        "info_list": [
          {"image_scene": "WB_DFT", "url": "http://..."},
          {"image_scene": "WB_PRV", "url": "http://..."}
        ]
      }
    ],
    "interact_info": {
      "liked": false,
      "liked_count": "18026",
      "collected": false,
      "collected_count": "3474",
      "comment_count": "265",
      "shared_count": "607"
    },
    "user": {
      "user_id": "584458606a6a69696e3b9472",
      "nickname": "控师地狱",
      "nick_name": "控师地狱",
      "avatar": "https://sns-avatar-qc.xhscdn.com/...",
      "xsec_token": "ABE_oRM-LPoZ7Hvz2p8oVZGbDK0DQMNL1cfm7-JGpbMSc="
    },
    "corner_tag_info": [
      {"type": "publish_time", "text": "2025-10-21"}
    ]
  }
}
```

## 5. 数据库表设计

对应以下 SQL 脚本：

- `xhs_notes` - 笔记主表
- `xhs_note_cards` - 笔记详情表
- `xhs_note_stats` - 互动统计数据
- `xhs_users` - 用户表
- `xhs_note_images` - 图片列表表

## 6. 字段类型转换注意

| 原始类型 | 数据库建议类型 | 说明 |
|----------|----------------|------|
| liked_count | BIGINT | 字符串数字需转换 |
| collected_count | BIGINT | 字符串数字需转换 |
| comment_count | BIGINT | 字符串数字需转换 |
| shared_count | BIGINT | 字符串数字需转换 |
| liked | TINYINT(1) | 布尔转 tinyint |
| collected | TINYINT(1) | 布尔转 tinyint |
| width/height | INT | 图片尺寸 |
