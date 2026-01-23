from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# 基础响应模型
class BaseResponse(BaseModel):
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="返回消息")
    data: Optional[Any] = Field(None, description="返回数据")

# Cookie相关模型
class CookieRequest(BaseModel):
    cookie: str = Field(..., description="小红书Cookie")
    key: Optional[str] = Field("default", description="Cookie标识，默认为default")

class CookieResponse(BaseModel):
    key: str = Field(..., description="Cookie标识")
    cookie: str = Field(..., description="小红书Cookie")

# 笔记爬取相关模型
class NoteRequest(BaseModel):
    note_url: str = Field(..., description="笔记链接")
    cookie_key: Optional[str] = Field("default", description="使用的Cookie标识")
    proxies: Optional[Dict[str, str]] = Field(None, description="代理配置")

class BatchNoteRequest(BaseModel):
    notes: List[str] = Field(..., description="笔记链接列表")
    save_choice: str = Field(default="all", description="保存选项: all, media, excel")
    excel_name: Optional[str] = Field(None, description="Excel文件名")
    cookie_key: Optional[str] = Field("default", description="使用的Cookie标识")
    proxies: Optional[Dict[str, str]] = Field(None, description="代理配置")

class UserNoteRequest(BaseModel):
    user_url: str = Field(..., description="用户主页链接")
    save_choice: str = Field(default="all", description="保存选项: all, media, excel")
    excel_name: Optional[str] = Field(None, description="Excel文件名")
    cookie_key: Optional[str] = Field("default", description="使用的Cookie标识")
    proxies: Optional[Dict[str, str]] = Field(None, description="代理配置")

class SearchRequest(BaseModel):
    query: str = Field(..., description="搜索关键词")
    require_num: int = Field(default=10, description="搜索数量")
    save_choice: str = Field(default="all", description="保存选项: all, media, excel")
    sort_type_choice: int = Field(default=0, description="排序方式: 0综合, 1最新, 2最多点赞, 3最多评论, 4最多收藏")
    note_type: int = Field(default=0, description="笔记类型: 0不限, 1视频, 2普通")
    note_time: int = Field(default=0, description="笔记时间: 0不限, 1一天内, 2一周内, 3半年内")
    note_range: int = Field(default=0, description="笔记范围: 0不限, 1已看过, 2未看过, 3已关注")
    pos_distance: int = Field(default=0, description="位置距离: 0不限, 1同城, 2附近")
    geo: Optional[Dict[str, float]] = Field(None, description="地理位置: {latitude: 纬度, longitude: 经度}")
    excel_name: Optional[str] = Field(None, description="Excel文件名")
    cookie_key: Optional[str] = Field("default", description="使用的Cookie标识")
    proxies: Optional[Dict[str, str]] = Field(None, description="代理配置")

# 结果响应模型
class NoteResponse(BaseResponse):
    data: Optional[Dict[str, Any]] = Field(None, description="笔记数据")

class BatchNoteResponse(BaseResponse):
    data: Optional[List[Dict[str, Any]]] = Field(None, description="笔记列表")

class SearchResponse(BaseResponse):
    data: Optional[List[str]] = Field(None, description="搜索结果笔记链接列表")
