import os
from loguru import logger
from spiders.data_spider import Data_Spider
from xhs_utils.common_util import init

if __name__ == '__main__':
    cookies_str, base_path = init()
    
    cookies_str = os.getenv("COOKIES")
    print(cookies_str)

    data_spider = Data_Spider(cookies_str)

    query = "菠萝"
    query_num = 10
    sort_type_choice = 0
    note_type = 0
    note_time = 0
    note_range = 0
    pos_distance = 0

    note_list, success, msg = data_spider.spider_some_search_note(
        query, query_num, cookies_str, base_path, 'all',
        sort_type_choice, note_type, note_time, note_range, pos_distance, geo=None
    )

    logger.info(f"搜索完成: success={success}, msg={msg}, 笔记数量={len(note_list)}")