# encoding: utf-8
import json
import requests
from xhs_utils.xhs_util import generate_request_params

COOKIES = "abRequestId=b13ea894-d51c-5b1f-ae2f-6aaf83c90e25; xsecappid=xhs-pc-web; a1=19d091705d4ocjrt8cun2b8c9zcmd093lkcj3zqal50000408871; webId=d805c3c542645cc77ac6008aee17a52c; gid=yjf8jyWyJy1Jyjf8jyW82TuAf4lSVF9YS7IJS01DYSjuSV286f8jqq88848YYWy8dfJJqJK2; web_session=040069b43fb4845faeb86bfa893b4bc3211675; id_token=VjEAAJdALr+J+5ah5uZjn7c8NWbGr1ZFQ843sq3sD2n4JVvVgmZNY98VTrB0jBCxrVSUiyENiz16S9RWiP5WVytxvkHhSnDgBOvwabiZCyPvqbEfL7SOgcv3WGgrX1wug/D7HoR9; webBuild=6.1.2; loadts=1773995407882; acw_tc=0a50892f17739954055287339e89bafd54ab1b81c6cd8d093eccbd04b0edd9; unread={%22ub%22:%2269bc9e69000000002200e420%22%2C%22ue%22:%2269a953cf000000001d013c5e%22%2C%22uc%22:33}; websectiga=16f444b9ff5e3d7e258b5f7674489196303a0b160e16647c6c2b4dcb609f4134; sec_poison_id=d74f50d4-48c3-4d16-8bf0-c2f77bf84081"
BASE_URL = "https://edith.xiaohongshu.com"
QUERY = "测试"

api = "/api/sns/web/v1/search/notes"
data = {
    "keyword": QUERY,
    "page": 1,
    "page_size": 20,
    "search_id": "2dn9they1jbjxwawlo4xd",
    "sort": "general",
    "note_type": 0,
    "ext_flags": [],
    "filters": [
        {"tags": ["general"], "type": "sort_type"},
        {"tags": ["不限"], "type": "filter_note_type"},
        {"tags": ["不限"], "type": "filter_note_time"},
        {"tags": ["不限"], "type": "filter_note_range"},
        {"tags": ["不限"], "type": "filter_pos_distance"}
    ],
    "geo": "",
    "image_formats": ["jpg", "webp", "avif"]
}

headers, cookies, data = generate_request_params(COOKIES, api, data, 'POST')
data = json.dumps(data, separators=(',', ':'), ensure_ascii=False)

print("=== Request Headers ===")
for k, v in headers.items():
    print(f"  {k}: {v[:80] if isinstance(v, str) and len(v) > 80 else v}")

print("\n=== Request Cookies ===")
for k, v in cookies.items():
    print(f"  {k}: {v[:80] if isinstance(v, str) and len(v) > 80 else v}")

print(f"\n=== Request Body ===\n{data}")

response = requests.post(BASE_URL + api, headers=headers, data=data.encode('utf-8'), cookies=cookies, proxies=None)
print(f"\n=== Response Status ===\n  status_code: {response.status_code}")
print(f"\n=== Response Headers ===")
for k, v in response.headers.items():
    if k.lower() not in ['content-encoding', 'transfer-encoding', 'connection']:
        print(f"  {k}: {v}")
print(f"\n=== Response Body ===")
try:
    res_json = response.json()
    print(json.dumps(res_json, ensure_ascii=False, indent=2))
except:
    print(response.text[:2000])