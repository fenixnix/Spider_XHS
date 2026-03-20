# Gradio 启动说明

## 快速启动

```powershell
.\gradio_app.ps1
```

或直接运行：

```powershell
python gradio_app.py
```

## 启动顺序

1. **先启动 FastAPI**（如果还没运行）：
   ```powershell
   .\fastapi_server.ps1
   ```

2. **再启动 Gradio**：
   ```powershell
   .\gradio_app.ps1
   ```

## 访问地址

- Gradio UI：http://localhost:7860
- FastAPI 文档：http://localhost:8000/docs

## 功能模块

| 标签页 | 功能 |
|--------|------|
| Cookie管理 | 设置/获取/删除小红书Cookie |
| 爬虫功能 | 单篇笔记、批量笔记、用户笔记、搜索 |
| 数据访问 | 查看爬取的媒体和Excel文件 |
