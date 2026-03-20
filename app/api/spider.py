from fastapi import APIRouter
import app.dependencies
from app.schemas import (
    BaseResponse, NoteRequest, BatchNoteRequest, UserNoteRequest, SearchRequest,
    NoteResponse, BatchNoteResponse, SearchResponse
)
from spiders.data_spider import Data_Spider
import os

router = APIRouter()

@router.get("/cookies", response_model=BaseResponse)
def get_cookie():
    """获取Cookie"""
    return {
        "success": True,
        "message": "获取Cookie成功" if app.dependencies.cookie else "Cookie未设置",
        "data": {"cookie": app.dependencies.cookie}
    }

@router.post("/cookies", response_model=BaseResponse)
def set_cookie(cookie_str: str):
    """设置Cookie"""
    app.dependencies.cookie = cookie_str
    return {
        "success": True,
        "message": "Cookie设置成功",
        "data": {"cookie": cookie_str}
    }

media_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../datas/media_datas'))
excel_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../datas/excel_datas'))

for base_path in [media_base_path, excel_base_path]:
    if not os.path.exists(base_path):
        os.makedirs(base_path)

base_path = {
    'media': media_base_path,
    'excel': excel_base_path,
}

data_spider = Data_Spider()

@router.post("/notes", response_model=NoteResponse)
def spider_note(request: NoteRequest):
    """爬取单个笔记信息"""
    if not app.dependencies.cookie:
        return {
            "success": False,
            "message": "请先设置Cookie",
            "data": None
        }

    try:
        success, msg, note_info = data_spider.spider_note(request.note_url, app.dependencies.cookie, request.proxies)
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
    if not app.dependencies.cookie:
        return {
            "success": False,
            "message": "请先设置Cookie",
            "data": None
        }

    try:
        data_spider.spider_some_note(request.notes, app.dependencies.cookie, base_path, request.save_choice, request.excel_name, request.proxies)

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
    if not app.dependencies.cookie:
        return {
            "success": False,
            "message": "请先设置Cookie",
            "data": None
        }

    try:
        note_list, success, msg = data_spider.spider_user_all_note(request.user_url, app.dependencies.cookie, base_path, request.save_choice, request.excel_name, request.proxies)

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
    if not app.dependencies.cookie:
        return {
            "success": False,
            "message": "请先设置Cookie",
            "data": None
        }

    try:
        note_list, success, msg = data_spider.spider_some_search_note(
            request.query, request.require_num, app.dependencies.cookie, base_path, request.save_choice,
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