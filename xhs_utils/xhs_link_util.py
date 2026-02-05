# encoding: utf-8
"""
小红书链接生成工具

功能:
- 通过 note_id 生成笔记链接
- 通过 user_id 生成用户主页链接

使用方法:
    from xhs_utils.xhs_link_util import note_url, user_url

    # 笔记链接
    url = note_url("68f71e060000000005011573")
    # https://www.xiaohongshu.com/explore/68f71e060000000005011573

    # 用户主页链接
    url = user_url("584458606a6a69696e3b9472")
    # https://www.xiaohongshu.com/user/profile/584458606a6a69696e3b9472
"""

import re


def note_url(note_id: str) -> str:
    """
    通过笔记ID生成小红书笔记链接

    Args:
        note_id: 笔记ID

    Returns:
        小红书笔记URL

    Examples:
        >>> note_url("68f71e060000000005011573")
        'https://www.xiaohongshu.com/explore/68f71e060000000005011573'
    """
    if not note_id:
        return ""
    return f"https://www.xiaohongshu.com/explore/{note_id}"


def note_url_from_xsec(
    note_id: str, xsec_token: str = "", xsec_source: str = "pc_search"
) -> str:
    """
    通过笔记ID和xsec_token生成小红书笔记链接（带完整参数）

    Args:
        note_id: 笔记ID
        xsec_token: 安全令牌
        xsec_source: 来源标识

    Returns:
        带参数的完整URL

    Examples:
        >>> note_url_from_xsec("68f71e06...", "ABxxx", "pc_search")
        'https://www.xiaohongshu.com/explore/68f71e06...?xsec_token=ABxxx&xsec_source=pc_search'
    """
    if not note_id:
        return ""

    base_url = f"https://www.xiaohongshu.com/explore/{note_id}"

    if xsec_token:
        params = f"xsec_token={xsec_token}"
        if xsec_source:
            params += f"&xsec_source={xsec_source}"
        return f"{base_url}?{params}"

    return base_url


def user_url(user_id: str) -> str:
    """
    通过用户ID生成小红书用户主页链接

    Args:
        user_id: 用户ID

    Returns:
        小红书用户主页URL

    Examples:
        >>> user_url("584458606a6a69696e3b9472")
        'https://www.xiaohongshu.com/user/profile/584458606a6a69696e3b9472'
    """
    if not user_id:
        return ""
    return f"https://www.xiaohongshu.com/user/profile/{user_id}"


def user_url_with_token(
    user_id: str, xsec_token: str = "", xsec_source: str = "pc_user"
) -> str:
    """
    通过用户ID和xsec_token生成小红书用户主页链接（带完整参数）

    Args:
        user_id: 用户ID
        xsec_token: 安全令牌
        xsec_source: 来源标识

    Returns:
        带参数的完整URL

    Examples:
        >>> user_url_with_token("58445860...", "ABxxx", "pc_user")
        'https://www.xiaohongshu.com/user/profile/58445860...?xsec_token=ABxxx&xsec_source=pc_user'
    """
    if not user_id:
        return ""

    base_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"

    if xsec_token:
        params = f"xsec_token={xsec_token}"
        if xsec_source:
            params += f"&xsec_source={xsec_source}"
        return f"{base_url}?{params}"

    return base_url


def is_valid_note_url(url: str) -> bool:
    """
    检查是否为有效的小红书笔记URL

    Args:
        url: URL字符串

    Returns:
        是否为有效的小红书笔记URL
    """
    if not url:
        return False
    pattern = r"https://www\.xiaohongshu\.com/explore/[a-zA-Z0-9]+"
    return bool(re.match(pattern, url))


def is_valid_user_url(url: str) -> bool:
    """
    检查是否为有效的小红书用户主页URL

    Args:
        url: URL字符串

    Returns:
        是否为有效的小红书用户主页URL
    """
    if not url:
        return False
    pattern = r"https://www\.xiaohongshu\.com/user/profile/[a-zA-Z0-9]+"
    return bool(re.match(pattern, url))


def extract_note_id(url: str) -> str:
    """
    从笔记URL中提取笔记ID

    Args:
        url: 笔记URL

    Returns:
        笔记ID

    Examples:
        >>> extract_note_id("https://www.xiaohongshu.com/explore/68f71e06...")
        '68f71e060000000005011573'
    """
    if not url:
        return ""
    match = re.search(r"/explore/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else ""


def extract_user_id(url: str) -> str:
    """
    从用户URL中提取用户ID

    Args:
        url: 用户主页URL

    Returns:
        用户ID

    Examples:
        >>> extract_user_id("https://www.xiaohongshu.com/user/profile/58445860...")
        '584458606a6a69696e3b9472'
    """
    if not url:
        return ""
    match = re.search(r"/profile/([a-zA-Z0-9]+)", url)
    return match.group(1) if match else ""


# =====================
# 便捷别名（兼容旧版本）
# =====================
generate_note_url = note_url
generate_user_url = user_url
