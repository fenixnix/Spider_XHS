from fastapi import APIRouter
from app.api import spider

router = APIRouter()

router.include_router(spider.router, prefix="", tags=["spider"])