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
# 创建一个简单的HTML索引文件
def create_index_html():
    index_path = os.path.join(datas_dir, "index.html")
    if not os.path.exists(index_path):
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>数据文件目录</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .folder { margin: 10px 0; }
        .folder a { color: #0066cc; text-decoration: none; font-weight: bold; }
        .folder a:hover { text-decoration: underline; }
        .note { color: #666; font-style: italic; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>数据文件目录</h1>
    <div class="folder">📁 <a href="/datas/media_datas/">media_datas/</a> - 媒体文件目录</div>
    <div class="folder">📁 <a href="/datas/excel_datas/">excel_datas/</a> - Excel文件目录</div>
    <div class="note">注意：点击文件夹名称查看内容</div>
</body>
</html>""")

create_index_html()
# 挂载静态文件目录，启用HTML模式
app.mount("/datas", StaticFiles(directory=datas_dir, html=True), name="datas")

# 注册API路由
app.include_router(api_router, prefix="/api")

# 根路径
@app.get("/")
def root():
    return {"message": "小红书爬虫API服务已启动", "docs": "/docs"}
