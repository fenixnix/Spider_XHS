from fastapi import APIRouter, HTTPException
from app.dependencies import cookie_manager
from app.schemas import CookieRequest, CookieResponse, BaseResponse

router = APIRouter()

@router.get("/", response_model=BaseResponse)
def get_cookies(key: str = "default"):
    """获取指定key的Cookie"""
    cookie = cookie_manager.get_cookie(key)
    if not cookie:
        return {
            "success": False,
            "message": f"未找到key为{key}的Cookie",
            "data": None
        }
    return {
        "success": True,
        "message": "获取Cookie成功",
        "data": CookieResponse(key=key, cookie=cookie)
    }

@router.post("/", response_model=BaseResponse)
def set_cookie(request: CookieRequest):
    """设置Cookie"""
    cookie_manager.set_cookie(request.cookie, request.key)
    return {
        "success": True,
        "message": f"Cookie已成功设置，key: {request.key}",
        "data": CookieResponse(key=request.key, cookie=request.cookie)
    }

@router.delete("/", response_model=BaseResponse)
def delete_cookie(key: str = "default"):
    """删除指定key的Cookie"""
    cookie_manager.delete_cookie(key)
    return {
        "success": True,
        "message": f"Cookie已成功删除，key: {key}",
        "data": None
    }

@router.get("/keys", response_model=BaseResponse)
def get_cookie_keys():
    """获取所有Cookie的key"""
    return {
        "success": True,
        "message": "获取Cookie keys成功",
        "data": list(cookie_manager._cookies.keys())
    }
