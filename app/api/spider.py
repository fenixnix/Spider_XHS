from fastapi import APIRouter, HTTPException
from app.dependencies import cookie_manager
from app.schemas import (
    BaseResponse, NoteRequest, BatchNoteRequest, UserNoteRequest, SearchRequest,
    NoteResponse, BatchNoteResponse, SearchResponse
)
from main import Data_Spider
import os

router = APIRouter()

# 初始化base_path，与原init函数保持一致
media_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../datas/media_datas'))
excel_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../datas/excel_datas'))

# 确保目录存在
for base_path in [media_base_path, excel_base_path]:
    if not os.path.exists(base_path):
        os.makedirs(base_path)

base_path = {
    'media': media_base_path,
    'excel': excel_base_path,
}

# 创建Data_Spider实例
data_spider = Data_Spider()

@router.post("/notes", response_model=NoteResponse)
def spider_note(request: NoteRequest):
    """爬取单个笔记信息"""
    cookie = cookie_manager.get_cookie(request.cookie_key)
    if not cookie:
        return {
            "success": False,
            "message": f"未找到cookie_key为{request.cookie_key}的Cookie，请先设置Cookie",
            "data": None
        }
    
    try:
        success, msg, note_info = data_spider.spider_note(request.note_url, cookie, request.proxies)
        return {
            "success": success,
            "message": msg,
            "data": note_info
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"爬取失败: {str(e)}",
            "data": None
        }

@router.post("/notes/batch", response_model=BatchNoteResponse)
def spider_some_note(request: BatchNoteRequest):
    """爬取多个笔记信息"""
    cookie = cookie_manager.get_cookie(request.cookie_key)
    if not cookie:
        return {
            "success": False,
            "message": f"未找到cookie_key为{request.cookie_key}的Cookie，请先设置Cookie",
            "data": None
        }
    
    try:
        # 调用原spider_some_note方法，该方法会自动保存文件
        data_spider.spider_some_note(request.notes, cookie, base_path, request.save_choice, request.excel_name, request.proxies)
        
        return {
            "success": True,
            "message": "批量爬取完成",
            "data": {
                "notes_count": len(request.notes),
                "save_choice": request.save_choice,
                "excel_name": request.excel_name,
                "media_path": base_path['media'],
                "excel_path": base_path['excel'],
                "access_url": f"/datas/excel_datas/{request.excel_name}.xlsx" if request.save_choice in ['all', 'excel'] else None
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"批量爬取失败: {str(e)}",
            "data": None
        }

@router.post("/users/notes", response_model=BaseResponse)
def spider_user_all_note(request: UserNoteRequest):
    """爬取用户所有笔记信息"""
    cookie = cookie_manager.get_cookie(request.cookie_key)
    if not cookie:
        return {
            "success": False,
            "message": f"未找到cookie_key为{request.cookie_key}的Cookie，请先设置Cookie",
            "data": None
        }
    
    try:
        # 调用原spider_user_all_note方法，该方法会自动保存文件
        note_list, success, msg = data_spider.spider_user_all_note(request.user_url, cookie, base_path, request.save_choice, request.excel_name, request.proxies)
        
        return {
            "success": success,
            "message": msg,
            "data": {
                "note_count": len(note_list),
                "save_choice": request.save_choice,
                "user_url": request.user_url,
                "media_path": base_path['media'],
                "excel_path": base_path['excel'],
                "access_url": f"/datas/excel_datas/{request.excel_name}.xlsx" if request.save_choice in ['all', 'excel'] else None
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"爬取用户笔记失败: {str(e)}",
            "data": None
        }

@router.post("/search", response_model=SearchResponse)
def spider_some_search_note(request: SearchRequest):
    """搜索笔记"""
    cookie = cookie_manager.get_cookie(request.cookie_key)
    if not cookie:
        return {
            "success": False,
            "message": f"未找到cookie_key为{request.cookie_key}的Cookie，请先设置Cookie",
            "data": None
        }
    
    try:
        # 调用原spider_some_search_note方法，该方法会自动保存文件
        note_list, success, msg = data_spider.spider_some_search_note(
            request.query, request.require_num, cookie, base_path, request.save_choice,
            request.sort_type_choice, request.note_type, request.note_time,
            request.note_range, request.pos_distance, request.geo,
            request.excel_name, request.proxies
        )
        
        return {
            "success": success,
            "message": msg,
            "data": {
                "note_count": len(note_list),
                "query": request.query,
                "save_choice": request.save_choice,
                "media_path": base_path['media'],
                "excel_path": base_path['excel'],
                "access_url": f"/datas/excel_datas/{request.excel_name}.xlsx" if request.save_choice in ['all', 'excel'] else None,
                "note_urls": note_list
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"搜索失败: {str(e)}",
            "data": None
        }
