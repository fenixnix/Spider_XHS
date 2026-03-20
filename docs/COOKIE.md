# 小红书 Cookie 整理

## Cookie 用途

以下 cookie 用于访问小红书网页版 API，可配合 Spider_XHS 项目使用。

## 使用方法

1. 打开浏览器，登录 [小红书](https://www.xiaohongshu.com)
2. 按 F12 打开开发者工具
3. 复制以下 cookie 字符串，填入项目的 `.env` 文件中：

```
COOKIES=你的cookie字符串
```

## Cookie 字符串

```
abRequestId=b13ea894-d51c-5b1f-ae2f-6aaf83c90e25; webBuild=6.1.2; xsecappid=xhs-pc-web; loadts=1773973997006; a1=19d091705d4ocjrt8cun2b8c9zcmd093lkcj3zqal50000408871; webId=d805c3c542645cc77ac6008aee17a52c; acw_tc=0a4ae0b517739739959565656e311429123a49675aaa6c940d454958d8cceb; websectiga=10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467; sec_poison_id=223ae978-0382-43ca-a6a1-a679986b5106; gid=yjf8jyWyJy1Jyjf8jyW82TuAf4lSVF9YS7IJS01DYSjuSV286f8jqq88848YYWy8dfJJqJK2; web_session=040069b43fb4845faeb86bfa893b4bc3211675; id_token=VjEAAJdALr+J+5ah5uZjn7c8NWbGr1ZFQ843sq3sD2n4JVvVgmZNY98VTrB0jBCxrVSUiyENiz16S9RWiP5WVytxvkHhSnDgBOvwabiZCyPvqbEfL7SOgcv3WGgrX1wug/D7HoR9; unread={%22ub%22:%2269b2e6a1000000002202d71a%22%2C%22ue%22:%2269b2b444000000002202d8ef%22%2C%22uc%22:23}
```

## Cookie 字段说明

| 字段 | 说明 |
|------|------|
| `abRequestId` | 请求追踪 ID |
| `webBuild` | 网页构建版本 |
| `xsecappid` | 安全应用标识 |
| `loadts` | 加载时间戳 |
| `a1` | 设备/浏览器指纹 |
| `webId` | Web 客户端 ID |
| `acw_tc` | 安全校验 token |
| `websectiga` | 安全签名 |
| `sec_poison_id` | 安全毒药 ID |
| `gid` | 全局会话 ID |
| `web_session` | Web 会话标识 |
| `id_token` | 身份认证 token |
| `unread` | 未读消息数统计 |

## 核心 Cookie 参数生成机制

小红书 Web 端 API 的 cookie 实际需要 **4 个核心参数**：

| 参数 | 获取方式 |
|------|----------|
| `xhsTrackerId` | 请求小红书主页时从 Set-Cookie 中获取 |
| `extra_exp_ids` | 请求小红书主页时从 Set-Cookie 中获取 |
| `timestamp2` | 需 POST 请求 `/fe_api/burdock/v2/shield/registerCanvas?p=cc` 获取 |
| `timestamp2.sig` | 需 POST 请求 `/fe_api/burdock/v2/shield/registerCanvas?p=cc` 获取 |

### 生成流程

1. **第一步**：请求 `https://www.xiaohongshu.com` 获取 `xhsTrackerId` 和 `extra_exp_ids`
2. **第二步**：携带第一步获取的 cookie，POST 请求以下接口获取 `timestamp2` 和 `timestamp2.sig`

```
POST https://www.xiaohongshu.com/fe_api/burdock/v2/shield/registerCanvas?p=cc
```

请求 data 参数：
```python
{
    'id': '<xhsTrackerId值>',
    'sign': '<浏览器UA及指纹信息拼接的签名>'
}
```

### Python 示例代码

```python
def get_xhs_cookie(proxies=None):
    url = 'https://www.xiaohongshu.com'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    }
    xhs_cookie = ''
    res = requests.get(url, headers=headers, verify=False, proxies=proxies, timeout=10)
    cookies = res.headers['Set-Cookie'].split(';')
    for cookie in cookies:
        if 'xhsTrackerId' in cookie or 'extra_exp_ids' in cookie:
            xhs_cookie += cookie + ';'

    url = 'https://www.xiaohongshu.com/fe_api/burdock/v2/shield/registerCanvas?p=cc'
    headers = {
        'Cookie': xhs_cookie,
        'User-Agent': headers['user-agent'],
    }
    data = {
        'id': '<xhsTrackerId>',
        'sign': '<UA及指纹签名>'
    }
    res = requests.post(url, headers=headers, data=data, verify=False, proxies=proxies, timeout=10)
    # 从响应中解析 timestamp2 和 timestamp2.sig
    return xhs_cookie
```

## 注意事项

- Cookie 具有时效性，过期后需重新获取
- 请勿将 cookie 泄露给他人
- 建议定期更换 cookie 以保证正常使用
- 频繁请求可能触发滑块验证，建议使用代理
