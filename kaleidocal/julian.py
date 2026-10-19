"""儒略日（Julian Day）核心 —— 所有历法的"中间货币"。

设计思想：无论多冷门的历法，都先换算成儒略日（一个连续的天数计数），
再从儒略日换算成目标历法。这样 N 种历法的互转只需 N 个「历法↔儒略日」
转换器，而不是 N×(N-1) 个两两转换。

儒略日约定：JD 的整数部分对应「正午 12:00」（儒略日最初的起点定义）。
因此 JDN = int(JD)，可直接用于干支纪日、星期等取模运算，无需额外偏移。

参考：Jean Meeus《Astronomical Algorithms》第 7 章。
"""
from __future__ import annotations

import math

__all__ = [
    "gregorian_to_jd",
    "jd_to_gregorian",
    "weekday_index",
    "weekday_name",
    "GREGORIAN_REFORM_JD",
]

# 1582-10-15 格里历改革：此日（含）起用格里历，此前用儒略历
GREGORIAN_REFORM_JD = 2299160.5

WEEKDAY_NAMES = ["日", "一", "二", "三", "四", "五", "六"]


def gregorian_to_jd(year: int, month: int, day: int, calendar: str = "auto") -> float:
    """公历/儒略历日期 → 儒略日（整数部分 = 正午）。

    参数:
        year: 天文纪年（公元 1 年 = 1，公元前 1 年 = 0，公元前 2 年 = -1……）
        month: 1-12
        day: 1-31（可为浮点，表示当日内的时刻）
        calendar: "auto" 按格里历改革自动切换；"gregorian"/"julian" 强制指定
    """
    if calendar == "auto":
        use_gregorian = (year, month, day) >= (1582, 10, 15)
    elif calendar == "gregorian":
        use_gregorian = True
    elif calendar == "julian":
        use_gregorian = False
    else:
        raise ValueError("calendar 必须是 'auto' / 'gregorian' / 'julian'")

    if month <= 2:
        year -= 1
        month += 12

    if use_gregorian:
        a = math.floor(year / 100)
        b = 2 - a + math.floor(a / 4)
    else:
        b = 0

    jd_midnight = (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + b
        - 1524.5
    )
    return jd_midnight + 0.5  # 转到正午基准


def jd_to_gregorian(jd: float, calendar: str = "auto") -> tuple:
    """儒略日 → 公历日期。

    返回 (year, month, day)，其中 day 为浮点数：整数部分为日，
    小数部分为该日内的时刻（0.5 即正午）。year 为天文纪年（<=0 表示公元前）。
    """
    jd = jd + 0.5
    z = math.floor(jd)
    f = jd - z

    if calendar == "auto":
        use_gregorian = z >= 2299161
    elif calendar == "gregorian":
        use_gregorian = True
    elif calendar == "julian":
        use_gregorian = False
    else:
        raise ValueError("calendar 必须是 'auto' / 'gregorian' / 'julian'")

    if use_gregorian:
        alpha = math.floor((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - math.floor(alpha / 4)
    else:
        a = z

    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)

    day = b - d - math.floor(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    return year, month, day


def weekday_index(jd: float) -> int:
    """儒略日 → 星期序号。0=星期日，1=星期一……6=星期六。"""
    return (math.floor(jd) + 1) % 7


def weekday_name(jd: float) -> str:
    """儒略日 → 中文星期名（"日" 表示星期日）。"""
    return WEEKDAY_NAMES[weekday_index(jd)]
