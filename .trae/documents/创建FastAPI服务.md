# 创建FastAPI服务计划

## 目录结构设计
```
Spider_XHS/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI入口文件
│   ├── api/             # API路由目录
│   │   ├── __init__.py
│   │   └── spider.py    # 爬虫功能API（包含cookie设置）
│   ├── services/        # 服务层
│   │   └── __init__.py
│   └── schemas/         # 请求/响应模型
│       └── __init__.py
├── datas/               # 结果文件目录（已有，由common_util.init()创建）
└── ...                  # 其他现有文件
```

## 核心功能实现

### 1. FastAPI入口文件 (`app/main.py`)
- 创建FastAPI实例
- 配置CORS
- 挂载datas目录为静态文件服务
- 注册API路由

### 2. 爬虫API (`app/api/spider.py`)
- 提供API端点，包含cookie设置功能：
  - `POST /api/cookie` - 设置爬虫cookie
  - `POST /api/notes` - 爬取单个笔记
  - `POST /api/notes/batch` - 爬取多个笔记
  - `POST /api/users/notes` - 爬取用户所有笔记
  - `POST /api/search` - 搜索笔记

### 3. 服务层 (`app/services/__init__.py`)
- 封装`Data_Spider`，实现：
  - 单例模式管理`Data_Spider`实例
  - 提供`set_cookie()`方法设置cookie
  - 调用原有`Data_Spider`方法执行爬虫任务
  - 管理datas目录路径

### 4. 数据模型 (`app/schemas/__init__.py`)
- 定义请求模型：
  - `CookieRequest` - Cookie设置请求
  - `NoteRequest` - 单个笔记请求
  - `BatchNoteRequest` - 批量笔记请求
  - `UserNoteRequest` - 用户笔记请求
  - `SearchRequest` - 搜索请求
- 定义响应模型：
  - `BaseResponse` - 基础响应模型
  - `NoteResponse` - 笔记响应
  - `SearchResponse` - 搜索响应

## 实现步骤

1. 创建必要的目录结构
2. 安装FastAPI依赖
3. 实现服务层，封装Data_Spider和cookie管理
4. 实现数据模型
5. 实现FastAPI入口文件
6. 实现爬虫API端点
7. 测试API功能

## 注意事项

- 保持代码模块化，遵循FastAPI最佳实践
- 确保API文档自动生成（Swagger UI）
- 处理好异常情况，返回友好的错误信息
- 挂载datas目录，方便用户获取结果文件
- 确保与现有代码兼容，不破坏原有功能
- cookie管理基于原有项目的逻辑，通过set_cookie方法设置