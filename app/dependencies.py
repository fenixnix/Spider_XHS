# Cookie存储管理
class CookieManager:
    def __init__(self):
        self._cookies = {}
    
    def get_cookie(self, key: str = "default") -> str:
        """获取指定key的cookie"""
        return self._cookies.get(key, "")
    
    def set_cookie(self, cookie: str, key: str = "default") -> None:
        """设置指定key的cookie"""
        self._cookies[key] = cookie
    
    def delete_cookie(self, key: str = "default") -> None:
        """删除指定key的cookie"""
        if key in self._cookies:
            del self._cookies[key]

# 创建全局Cookie管理器实例
cookie_manager = CookieManager()
