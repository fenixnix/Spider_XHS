import os
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis
from xhs_utils.data_util import handle_note_info, download_note, save_to_xlsx


class Data_Spider():
    def __init__(self, cookies_str: str = None):
        self._cookies = cookies_str
        self.xhs_apis = XHS_Apis()

    def set_cookies(self, cookies_str: str):
        self._cookies = cookies_str

    def _get_cookies(self, cookies_str: str = None) -> str:
        if cookies_str is not None:
            self._cookies = cookies_str
        return self._cookies

    def spider_note(self, note_url: str, cookies_str: str = None, proxies=None):
        cookies = self._get_cookies(cookies_str)
        note_info = None
        try:
            success, msg, note_info = self.xhs_apis.get_note_info(note_url, cookies, proxies)
            if success:
                note_info = note_info['data']['items'][0]
                note_info['url'] = note_url
                note_info = handle_note_info(note_info)
        except Exception as e:
            success = False
            msg = str(e)
        logger.info(f'爬取笔记信息 {note_url}: {success}, msg: {msg}')
        return success, msg, note_info

    def spider_some_note(self, notes: list, cookies_str: str = None, base_path: dict = None, save_choice: str = 'all', excel_name: str = '', proxies=None):
        cookies = self._get_cookies(cookies_str)
        if (save_choice == 'all' or save_choice == 'excel') and excel_name == '':
            raise ValueError('excel_name 不能为空')
        note_list = []
        for note_url in notes:
            success, msg, note_info = self.spider_note(note_url, cookies, proxies)
            print("MSG:",msg)
            if note_info is not None and success:
                note_list.append(note_info)
        for note_info in note_list:
            if save_choice == 'all' or 'media' in save_choice:
                download_note(note_info, base_path['media'], save_choice)
        if save_choice == 'all' or save_choice == 'excel':
            file_path = os.path.abspath(os.path.join(base_path['excel'], f'{excel_name}.xlsx'))
            save_to_xlsx(note_list, file_path)

    def spider_user_all_note(self, user_url: str, cookies_str: str = None, base_path: dict = None, save_choice: str = 'all', excel_name: str = '', proxies=None):
        cookies = self._get_cookies(cookies_str)
        note_list = []
        try:
            success, msg, all_note_info = self.xhs_apis.get_user_all_notes(user_url, cookies, proxies)
            if success:
                logger.info(f'用户 {user_url} 作品数量: {len(all_note_info)}')
                for simple_note_info in all_note_info:
                    note_url = f"https://www.xiaohongshu.com/explore/{simple_note_info['note_id']}?xsec_token={simple_note_info['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = user_url.split('/')[-1].split('?')[0]
            self.spider_some_note(note_list, cookies, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = str(e)
        logger.info(f'爬取用户所有视频 {user_url}: {success}, msg: {msg}')
        return note_list, success, msg

    def spider_some_search_note(self, query: str, require_num: int, cookies_str: str = None, base_path: dict = None, save_choice: str = 'all', sort_type_choice=0, note_type=0, note_time=0, note_range=0, pos_distance=0, geo: dict = None,  excel_name: str = '', proxies=None):
        cookies = self._get_cookies(cookies_str)
        note_list = []
        try:
            success, msg, notes = self.xhs_apis.search_some_note(query, require_num, cookies, sort_type_choice, note_type, note_time, note_range, pos_distance, geo, proxies)
            print("MSG:")
            print(msg)
            if success:
                notes = list(filter(lambda x: x['model_type'] == "note", notes))
                logger.info(f'搜索关键词 {query} 笔记数量: {len(notes)}')
                for note in notes:
                    note_url = f"https://www.xiaohongshu.com/explore/{note['id']}?xsec_token={note['xsec_token']}"
                    note_list.append(note_url)
            if save_choice == 'all' or save_choice == 'excel':
                excel_name = query
            self.spider_some_note(note_list, cookies, base_path, save_choice, excel_name, proxies)
        except Exception as e:
            success = False
            msg = str(e)
        logger.info(f'搜索关键词 {query} 笔记: {success}, msg: {msg}')
        return note_list, success, msg