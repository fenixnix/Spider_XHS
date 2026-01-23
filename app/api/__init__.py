from fastapi import APIRouter
from app.api import cookies, spider

# 创建主路由
router = APIRouter()

# 包含各个子路由
router.include_router(cookies.router, prefix="/cookies", tags=["cookies"])
router.include_router(spider.router, prefix="", tags=["spider"])
