import json
import hashlib
import base64
from Crypto.Cipher import AES

def generate_xs(a1, api, data=''):
    """
    生成小红书创作者平台的xs签名
    :param a1: cookie中的a1值
    :param api: API路径
    :param data: 请求数据
    :return: xs, xt, data
    """
    # 固定密钥和IV
    key = b'7cc4adla5ay0701v'
    iv = b'4uzjr7mbsibcaldp'
    
    def encrypt(data):
        """AES-128-CBC加密"""
        # 填充数据，使其长度为16的倍数
        pad_len = 16 - (len(data) % 16)
        data = data + chr(pad_len) * pad_len
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(data.encode('utf-8'))
        return encrypted.hex()
    
    # 构建api字符串
    api_str = 'url=' + api
    if data:
        api_str += json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    
    # 生成x1（MD5哈希）
    x1 = hashlib.md5(api_str.encode('utf-8')).hexdigest()
    
    # 固定x2值
    x2 = "0|0|0|1|0|0|1|0|0|0|1|0|0|0|0|1|0|0|0"
    
    # x3是a1值
    x3 = a1
    
    # x4是当前时间戳
    import time
    x4 = str(int(time.time() * 1000))
    
    # 组合参数
    x = f'x1={x1};x2={x2};x3={x3};x4={x4};'
    
    # base64编码
    x_b64 = base64.b64encode(x.encode('utf-8')).decode('utf-8')
    
    # AES加密
    payload = encrypt(x_b64)
    
    # 构建加密数据
    encrypt_data = {
        "signSvn": "56",
        "signType": "x2",
        "appId": "ugc",
        "signVersion": "1",
        "payload": payload
    }
    
    # JSON序列化并base64编码
    encrypt_data_str = json.dumps(encrypt_data, separators=(',', ':'), ensure_ascii=False)
    encrypt_data_b64 = base64.b64encode(encrypt_data_str.encode('utf-8')).decode('utf-8')
    
    # 添加前缀
    xs = 'XYW_' + encrypt_data_b64
    xt = x4
    
    # 如果data非空，确保其为JSON字符串
    if data and isinstance(data, dict):
        data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    
    return xs, xt, data


def get_common_headers():
    return {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
        "accept": "application/json, text/plain, */*",
        "Host": "edith.xiaohongshu.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "sec-ch-ua-platform": "\"Windows\"",
        "authorization": "",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Microsoft Edge\";v=\"138\"",
        "sec-ch-ua-mobile": "?0",
        "x-t": "",
        "x-s": "",
        "origin": "https://creator.xiaohongshu.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://creator.xiaohongshu.com/",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "priority": "u=1, i"
    }


def splice_str(api, params):
    url = api + '?'
    for key, value in params.items():
        if value is None:
            value = ''
        url += key + '=' + value + '&'
    return url[:-1]