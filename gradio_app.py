import gradio as gr
import requests
import json

# FastAPI服务地址
API_BASE_URL = "http://localhost:8000/api"

# 数据根目录URL
DATA_ROOT_URL = "http://localhost:8000/datas"

# 定义API请求函数
def call_api(endpoint, method="GET", data=None, params=None):
    """调用FastAPI接口"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        else:
            response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"请求失败: {str(e)}",
            "data": None
        }

# Cookie管理函数
def set_cookie(cookie, key="default"):
    """设置Cookie"""
    data = {"cookie": cookie, "key": key}
    result = call_api("/cookies", method="POST", data=data)
    return f"状态: {'成功' if result['success'] else '失败'}\n消息: {result['message']}"

def get_cookie(key="default"):
    """获取Cookie"""
    result = call_api("/cookies", params={"key": key})
    if result['success']:
        cookie = result['data']['cookie']
        return f"Cookie获取成功 (key: {key}):\n{cookie}"
    else:
        return f"状态: 失败\n消息: {result['message']}"

def delete_cookie(key="default"):
    """删除Cookie"""
    result = call_api("/cookies", method="DELETE", params={"key": key})
    return f"状态: {'成功' if result['success'] else '失败'}\n消息: {result['message']}"

# 爬虫功能函数
def spider_single_note(note_url, cookie_key="default"):
    """爬取单个笔记"""
    data = {
        "note_url": note_url,
        "cookie_key": cookie_key
    }
    result = call_api("/notes", method="POST", data=data)
    if result['success']:
        note_info = result['data']
        return f"状态: 成功\n笔记信息: {json.dumps(note_info, ensure_ascii=False, indent=2)}"
    else:
        return f"状态: 失败\n消息: {result['message']}"

def spider_batch_notes(notes_text, save_choice="all", excel_name="batch_notes", cookie_key="default"):
    """爬取多个笔记"""
    notes = [line.strip() for line in notes_text.split("\n") if line.strip()]
    if not notes:
        return "请输入有效的笔记链接列表"
    
    data = {
        "notes": notes,
        "save_choice": save_choice,
        "excel_name": excel_name,
        "cookie_key": cookie_key
    }
    result = call_api("/notes/batch", method="POST", data=data)
    if result['success']:
        data_info = result['data']
        access_url = data_info.get('access_url')
        return f"状态: 成功\n消息: 批量爬取完成\n笔记数量: {data_info['notes_count']}\n保存选项: {data_info['save_choice']}\n\n文件保存位置:\n- 媒体文件: {data_info['media_path']}\n- Excel文件: {data_info['excel_path']}\n\n可访问链接: {f'{DATA_ROOT_URL}{access_url}' if access_url else '无Excel文件'}"
    else:
        return f"状态: 失败\n消息: {result['message']}"

def spider_user_notes(user_url, save_choice="all", excel_name="", cookie_key="default"):
    """爬取用户所有笔记"""
    data = {
        "user_url": user_url,
        "save_choice": save_choice,
        "excel_name": excel_name,
        "cookie_key": cookie_key
    }
    result = call_api("/users/notes", method="POST", data=data)
    if result['success']:
        data_info = result['data']
        access_url = data_info.get('access_url')
        return f"状态: 成功\n消息: {result['message']}\n笔记数量: {data_info['note_count']}\n保存选项: {data_info['save_choice']}\n\n文件保存位置:\n- 媒体文件: {data_info['media_path']}\n- Excel文件: {data_info['excel_path']}\n\n可访问链接: {f'{DATA_ROOT_URL}{access_url}' if access_url else '无Excel文件'}"
    else:
        return f"状态: 失败\n消息: {result['message']}"

def spider_search_notes(
    query, 
    require_num=10, 
    save_choice="all", 
    sort_type_choice=0, 
    note_type=0, 
    note_time=0, 
    note_range=0, 
    pos_distance=0,
    excel_name="", 
    cookie_key="default"
):
    """搜索笔记"""
    data = {
        "query": query,
        "require_num": require_num,
        "save_choice": save_choice,
        "sort_type_choice": sort_type_choice,
        "note_type": note_type,
        "note_time": note_time,
        "note_range": note_range,
        "pos_distance": pos_distance,
        "excel_name": excel_name,
        "cookie_key": cookie_key
    }
    result = call_api("/search", method="POST", data=data)
    if result['success']:
        data_info = result['data']
        access_url = data_info.get('access_url')
        return f"状态: 成功\n消息: {result['message']}\n搜索关键词: {data_info['query']}\n找到笔记数量: {data_info['note_count']}\n保存选项: {data_info['save_choice']}\n\n文件保存位置:\n- 媒体文件: {data_info['media_path']}\n- Excel文件: {data_info['excel_path']}\n\n可访问链接: {f'{DATA_ROOT_URL}{access_url}' if access_url else '无Excel文件'}\n\n笔记链接列表:\n" + "\n".join(data_info['note_urls'])
    else:
        return f"状态: 失败\n消息: {result['message']}"

# 创建Gradio界面
with gr.Blocks(title="小红书爬虫API", theme=gr.themes.Soft()) as app:
    # 标题和说明
    gr.Markdown("# 小红书爬虫API工具")
    gr.Markdown("## 基于FastAPI的小红书爬虫服务")
    gr.Markdown(f"### 数据根目录访问: [点击访问]({DATA_ROOT_URL})\n")
    
    # Cookie管理标签页
    with gr.Tab("Cookie管理"):
        gr.Markdown("#### 设置Cookie")
        with gr.Row():
            cookie_input = gr.Textbox(label="小红书Cookie", placeholder="请输入完整的小红书Cookie", lines=3)
            cookie_key_input = gr.Textbox(label="Cookie标识", value="default", placeholder="默认为default")
        set_cookie_btn = gr.Button("设置Cookie")
        set_cookie_output = gr.Textbox(label="设置结果", lines=2)
        
        gr.Markdown("#### 获取Cookie")
        with gr.Row():
            get_cookie_key = gr.Textbox(label="Cookie标识", value="default")
            get_cookie_btn = gr.Button("获取Cookie")
        get_cookie_output = gr.Textbox(label="获取结果", lines=3)
        
        gr.Markdown("#### 删除Cookie")
        with gr.Row():
            delete_cookie_key = gr.Textbox(label="Cookie标识", value="default")
            delete_cookie_btn = gr.Button("删除Cookie")
        delete_cookie_output = gr.Textbox(label="删除结果", lines=2)
    
    # 爬虫功能标签页
    with gr.Tab("爬虫功能"):
        # 爬取单个笔记
        gr.Markdown("#### 爬取单个笔记")
        with gr.Row():
            single_note_url = gr.Textbox(label="笔记链接", placeholder="请输入小红书笔记链接")
            single_cookie_key = gr.Textbox(label="Cookie标识", value="default")
        single_note_btn = gr.Button("爬取单个笔记")
        single_note_output = gr.Textbox(label="爬取结果", lines=5)
        
        # 爬取多个笔记
        gr.Markdown("#### 爬取多个笔记")
        batch_notes_text = gr.Textbox(label="笔记链接列表", placeholder="每行一个笔记链接", lines=5)
        with gr.Row():
            batch_save_choice = gr.Dropdown(
                choices=["all", "media", "excel"], 
                label="保存选项", 
                value="all",
                info="all: 保存所有信息, media: 保存媒体文件, excel: 保存到Excel"
            )
            batch_excel_name = gr.Textbox(label="Excel文件名", value="batch_notes", placeholder="保存到Excel时的文件名")
            batch_cookie_key = gr.Textbox(label="Cookie标识", value="default")
        batch_notes_btn = gr.Button("批量爬取笔记")
        batch_notes_output = gr.Textbox(label="爬取结果", lines=5)
        
        # 爬取用户所有笔记
        gr.Markdown("#### 爬取用户所有笔记")
        with gr.Row():
            user_url = gr.Textbox(label="用户主页链接", placeholder="请输入小红书用户主页链接")
            user_save_choice = gr.Dropdown(
                choices=["all", "media", "excel"], 
                label="保存选项", 
                value="all"
            )
        with gr.Row():
            user_excel_name = gr.Textbox(label="Excel文件名", placeholder="可选，默认为用户ID")
            user_cookie_key = gr.Textbox(label="Cookie标识", value="default")
        user_notes_btn = gr.Button("爬取用户所有笔记")
        user_notes_output = gr.Textbox(label="爬取结果", lines=5)
        
        # 搜索笔记
        gr.Markdown("#### 搜索笔记")
        with gr.Row():
            search_query = gr.Textbox(label="搜索关键词", placeholder="请输入搜索关键词")
            search_num = gr.Number(label="搜索数量", value=10, minimum=1, maximum=100)
        with gr.Row():
            search_save_choice = gr.Dropdown(
                choices=["all", "media", "excel"], 
                label="保存选项", 
                value="all"
            )
            search_excel_name = gr.Textbox(label="Excel文件名", placeholder="可选，默认为搜索关键词")
        with gr.Row():
            search_sort = gr.Dropdown(
                choices=[("综合排序", 0), ("最新", 1), ("最多点赞", 2), ("最多评论", 3), ("最多收藏", 4)],
                label="排序方式",
                value=0
            )
            search_note_type = gr.Dropdown(
                choices=[("不限", 0), ("视频笔记", 1), ("普通笔记", 2)],
                label="笔记类型",
                value=0
            )
        with gr.Row():
            search_note_time = gr.Dropdown(
                choices=[("不限", 0), ("一天内", 1), ("一周内", 2), ("半年内", 3)],
                label="笔记时间",
                value=0
            )
            search_cookie_key = gr.Textbox(label="Cookie标识", value="default")
        search_btn = gr.Button("搜索笔记")
        search_output = gr.Textbox(label="搜索结果", lines=5)
    
    # 数据访问标签页
    with gr.Tab("数据访问"):
        gr.Markdown("### 数据文件访问")
        gr.Markdown(f"#### 数据根目录: [点击访问]({DATA_ROOT_URL})\n")
        gr.Markdown("- 媒体文件保存在: `media_datas` 目录")
        gr.Markdown("- Excel文件保存在: `excel_datas` 目录")
        gr.Markdown("#### 示例访问链接:")
        gr.Markdown(f"- 示例Excel文件: {DATA_ROOT_URL}/excel_datas/test.xlsx")
        gr.Markdown(f"- 示例媒体文件: {DATA_ROOT_URL}/media_datas/xxx.jpg")
    
    # 设置事件监听
    # Cookie管理事件
    set_cookie_btn.click(set_cookie, inputs=[cookie_input, cookie_key_input], outputs=set_cookie_output)
    get_cookie_btn.click(get_cookie, inputs=[get_cookie_key], outputs=get_cookie_output)
    delete_cookie_btn.click(delete_cookie, inputs=[delete_cookie_key], outputs=delete_cookie_output)
    
    # 爬虫功能事件
    single_note_btn.click(spider_single_note, inputs=[single_note_url, single_cookie_key], outputs=single_note_output)
    batch_notes_btn.click(spider_batch_notes, inputs=[batch_notes_text, batch_save_choice, batch_excel_name, batch_cookie_key], outputs=batch_notes_output)
    user_notes_btn.click(spider_user_notes, inputs=[user_url, user_save_choice, user_excel_name, user_cookie_key], outputs=user_notes_output)
    search_btn.click(spider_search_notes, inputs=[
        search_query, search_num, search_save_choice, search_sort, 
        search_note_type, search_note_time, gr.Number(value=0), gr.Number(value=0), 
        search_excel_name, search_cookie_key
    ], outputs=search_output)
    
    # 底部信息
    gr.Markdown("\n---\n### 注意事项")
    gr.Markdown("1. 请先设置有效的小红书Cookie")
    gr.Markdown("2. 笔记链接可能会过期，请使用最新的链接")
    gr.Markdown("3. 批量爬取和用户爬取可能需要较长时间")
    gr.Markdown("4. 结果文件会保存在datas目录，可通过数据根目录访问")

# 运行Gradio应用
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )
