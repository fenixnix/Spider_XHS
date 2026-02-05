# fetch_by_subject.py 功能设计文档

## 1. 功能概述

通过关键词批量搜索小红书笔记，边采集边保存到 JSONL 文件。

## 2. 命令行参数

### 核心参数

| 参数 | 简写 | 类型 | 默认值 | 说明 |
|------|------|------|--------|------|
| subtitle | - | str | 必填 | 搜索关键词 |
| quantity | -n | int | 100 | 采集数量 |
| output | -o | str | `{subtitle}.jsonl` | 输出文件名 |

### 可选筛选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| sort | int | 0 | 排序: 0-综合, 1-最新, 2-点赞, 3-评论, 4-收藏 |
| type | int | 0 | 类型: 0-不限, 1-视频, 2-图文 |
| time | int | 0 | 时间: 0-不限, 1-一天, 2-一周, 3-半年 |

### 使用示例

```bash
# 默认：搜索"美妆"，100条
python fetch_by_subject.py "美妆"

# 指定数量
python fetch_by_subject.py "美食" -n 200

# 指定输出文件
python fetch_by_subject.py "穿搭" -o "chuan_da.jsonl"

# 完整参数
python fetch_by_subject.py "护肤" -n 500 -o "skin_care.jsonl" --sort 2 --type 2 --time 1
```

## 3. 实现代码

```python
import argparse
import json
import random
import re
import time
from datetime import datetime

from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.common_util import init
from loguru import logger


def random_sleep(min_sec: float = 2.0, max_sec: float = 5.0):
    """随机休眠，模拟人类节奏"""
    time.sleep(random.uniform(min_sec, max_sec))


def fetch_notes_by_subject(
    subtitle: str,
    quantity: int = 100,
    output: str = None,
    sort: int = 0,
    note_type: int = 0,
    note_time: int = 0
):
    """
    根据主题批量采集小红书笔记

    Returns:
        tuple: (success: bool, msg: str, file_path: str)
    """
    cookies_str, base_path = init()
    xhs_apis = XHS_Apis()

    # 设置输出文件
    if not output:
        safe_name = re.sub(r'[\\/:*?"<>|]', '_', subtitle)
        output = f'{safe_name}.jsonl'
    file_path = os.path.abspath(os.path.join(base_path['excel'], output))

    page = 1
    total_count = 0

    logger.info(f'开始采集: {subtitle}, 目标: {quantity}, 输出: {file_path}')

    try:
        while total_count < quantity:
            # 请求前随机休眠
            random_sleep(2.0, 5.0)

            success, msg, notes = xhs_apis.search_note(
                query=subtitle,
                cookies_str=cookies_str,
                page=page,
                sort_type_choice=sort,
                note_type=note_type,
                note_time=note_time
            )

            if not success:
                logger.warning(f'第 {page} 页失败: {msg}')
                random_sleep(10.0, 20.0)
                continue

            if not notes:
                logger.info(f'第 {page} 页无数据')
                break

            # 实时保存到 JSONL
            for note in notes:
                with open(file_path, 'a', encoding='utf-8') as f:
                    note['crawl_time'] = datetime.now().isoformat()
                    f.write(json.dumps(note, ensure_ascii=False) + '\n')
                total_count += 1

                if total_count >= quantity:
                    break

            logger.info(f'第 {page} 页完成，累计 {total_count} 条')
            page += 1

            # 翻页后增加间隔
            random_sleep(3.0, 8.0)

    except Exception as e:
        logger.error(f'采集异常: {e}')
        return False, str(e), file_path

    logger.info(f'采集完成: {subtitle}, 共 {total_count} 条')
    return True, f'成功采集 {total_count} 条', file_path


def main():
    parser = argparse.ArgumentParser(description='小红书笔记批量采集工具')
    parser.add_argument('subtitle', type=str, help='搜索关键词')
    parser.add_argument('--quantity', '-n', type=int, default=100, help='采集数量')
    parser.add_argument('--output', '-o', type=str, default=None, help='输出文件名')
    parser.add_argument('--sort', type=int, default=0, choices=[0,1,2,3,4],
                        help='排序: 0-综合, 1-最新, 2-点赞, 3-评论, 4-收藏')
    parser.add_argument('--type', type=int, default=0, choices=[0,1,2],
                        help='类型: 0-不限, 1-视频, 2-图文')
    parser.add_argument('--time', type=int, default=0, choices=[0,1,2,3],
                        help='时间: 0-不限, 1-一天, 2-一周, 3-半年')

    args = parser.parse_args()

    success, msg, file_path = fetch_notes_by_subject(
        subtitle=args.subtitle,
        quantity=args.quantity,
        output=args.output,
        sort=args.sort,
        note_type=args.type,
        note_time=args.time
    )

    if success:
        print(f'\n✅ {msg}')
        print(f'📁 {file_path}')
    else:
        print(f'\n❌ {msg}')
        exit(1)


if __name__ == '__main__':
    main()
```

## 4. 输出格式

JSONL（JSON Lines），每行一条 JSON，实时追加写入。

## 5. 随机休眠策略

| 场景 | 间隔 |
|------|------|
| 请求前 | 2-5 秒 |
| 翻页后 | 3-8 秒 |
| 失败重试 | 10-20 秒 |

## 6. 注意事项

1. 确保 `.env` 已配置有效 COOKIES
2. 必须使用随机间隔，避免固定频率
3. 返回原始数据结构，待实际测试后确认
