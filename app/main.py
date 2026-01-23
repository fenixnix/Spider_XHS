from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import router as api_router

# 创建FastAPI实例
app = FastAPI(
    title="小红书爬虫API",
    description="提供小红书笔记爬取、用户笔记爬取和搜索功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 挂载datas目录，方便用户获取结果文件
import os
# 使用绝对路径确保挂载正确
datas_dir = os.path.abspath("datas")
# 确保目录存在
if not os.path.exists(datas_dir):
    os.makedirs(datas_dir)
# 挂载静态文件目录
app.mount("/datas", StaticFiles(directory=datas_dir), name="datas")

# 注册API路由
app.include_router(api_router, prefix="/api")

# 根路径
@app.get("/")
def root():
    return {"message": "小红书爬虫API服务已启动", "docs": "/docs"}
