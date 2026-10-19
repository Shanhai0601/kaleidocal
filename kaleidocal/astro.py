"""天文算法：太阳视黄经（节气）与新月（朔）时刻。

基于 Jean Meeus《Astronomical Algorithms》第 25 章（太阳）与第 49 章（月相）。
纯算法、无外部数据表，精度约 ±1 分钟，足以确定二十四节气与农历朔望。

历法背景：农历的"定气定朔"正是靠这两个量排出来的——
以太阳视黄经每 15° 定节气、以日月黄经相合定朔，而不是人为约定。
"""
from __future__ import annotations

import math
from functools import lru_cache

from kaleidocal.julian import gregorian_to_jd

__all__ = [
    "solar_apparent_longitude",
    "solar_term_jd",
    "new_moon_jd",
    "new_moon_before",
    "SOLAR_TERMS",
    "MAJOR_TERMS",
]

# 24 节气名，按太阳视黄经 0°（春分）起、每 15° 一个
SOLAR_TERMS = [
    "春分", "清明", "谷雨", "立夏", "小满", "芒种",
    "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪",
    "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰",
]

# 12 个中气（黄经 30° 的整数倍，即偶数序号的节气），用于农历定月
# 序号即 0=春分 … 9=冬至 … 11=雨水
MAJOR_TERMS = [
    "春分", "谷雨", "小满", "夏至", "大暑", "处暑",
    "秋分", "霜降", "小雪", "冬至", "大寒", "雨水",
]

# 每个节气的平均公历日期（月, 日），用于定位二分求根区间
_TERM_APPROX = [
    (3, 20), (4, 5), (4, 20), (5, 6), (5, 21), (6, 6),
    (6, 21), (7, 7), (7, 23), (8, 8), (8, 23), (9, 8),
    (9, 23), (10, 8), (10, 23), (11, 7), (11, 22), (12, 7),
    (12, 22), (1, 6), (1, 20), (2, 4), (2, 19), (3, 6),
]


def solar_apparent_longitude(jde: float) -> float:
    """给定儒略历书日 JDE，返回太阳视黄经（度，0-360）。

    采用 Meeus 的低精度太阳理论（含光行差与章动的简化修正），
    精度约 0.01°，对应时间误差 < 1 分钟，对节气判定绰绰有余。
    """
    t = (jde - 2451545.0) / 36525.0
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = 357.52911 + 35999.05029 * t - 0.0001537 * t * t
    c = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(math.radians(m))
        + (0.019993 - 0.000101 * t) * math.sin(math.radians(2 * m))
        + 0.000289 * math.sin(math.radians(3 * m))
    )
    true_long = l0 + c
    omega = 125.04 - 1934.136 * t
    apparent = true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))
    return apparent % 360.0


def _longitude_diff(jde: float, target: float) -> float:
    """太阳视黄经与目标角度的差值，归一化到 [-180, 180)。"""
    lon = solar_apparent_longitude(jde)
    return (lon - target + 180.0) % 360.0 - 180.0


@lru_cache(maxsize=2048)
def solar_term_jd(year: int, k: int) -> float:
    """返回公历 year 年第 k 个节气的儒略历书日 JDE。

    k: 0=春分 … 18=冬至 … 23=惊蛰（即黄经 = 15°×k）。
    在平均日期 ±18 天的区间内二分求根，40 次迭代收敛到秒级。
    """
    if not 0 <= k <= 23:
        raise ValueError("k 必须在 0..23")
    target = 15.0 * k
    m, d = _TERM_APPROX[k]
    base = gregorian_to_jd(year, m, d)
    lo = base - 18.0
    hi = base + 18.0
    # 保证 lo 端差值 < 0、hi 端差值 > 0（黄经随天数单调递增）
    while _longitude_diff(lo, target) > 0:
        lo -= 1.0
    while _longitude_diff(hi, target) < 0:
        hi += 1.0
    for _ in range(50):
        mid = (lo + hi) / 2.0
        if _longitude_diff(mid, target) >= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


def _moon_index(jde: float) -> float:
    """给定 JDE，返回最接近的 Meeus 月相编号 k 的浮点估计。"""
    return (jde - 2451550.09766) / 29.530588861


@lru_cache(maxsize=4096)
def new_moon_jd(k: int) -> float:
    """返回第 k 个新月（朔）的儒略历书日 JDE。

    Meeus 第 49 章新月公式，含主周期项修正（行星项省略，误差 < 1 分钟）。
    """
    t = k / 1236.85
    jde = (
        2451550.09766
        + 29.530588861 * k
        + 0.00015437 * t * t
        - 0.000000150 * t ** 3
        + 0.00000000073 * t ** 4
    )
    e = 1 - 0.002516 * t - 0.0000074 * t * t
    m = math.radians(2.5534 + 29.10535670 * k - 0.0000014 * t * t - 0.00000011 * t ** 3)
    mp = math.radians(
        201.564192 + 385.81693528 * k + 0.0107582 * t * t
        + 0.00001238 * t ** 3 - 0.000000058 * t ** 4
    )
    f = math.radians(
        160.7108 + 390.67050284 * k - 0.0016118 * t * t
        - 0.00000227 * t ** 3 + 0.000000011 * t ** 4
    )
    omega = math.radians(
        124.7746 - 1.56375588 * k + 0.0020672 * t * t + 0.00000215 * t ** 3
    )

    corr = (
        -0.40720 * math.sin(mp)
        + 0.17241 * e * math.sin(m)
        + 0.01608 * math.sin(2 * mp)
        + 0.01039 * math.sin(2 * f)
        + 0.00739 * e * math.sin(mp - m)
        - 0.00514 * e * math.sin(mp + m)
        + 0.00208 * e * e * math.sin(2 * m)
        - 0.00111 * math.sin(mp - 2 * f)
        - 0.00057 * math.sin(mp + 2 * f)
        + 0.00056 * e * math.sin(2 * mp + m)
        - 0.00042 * math.sin(3 * mp)
        + 0.00042 * e * math.sin(m + 2 * f)
        + 0.00038 * e * math.sin(m - 2 * f)
        - 0.00024 * e * math.sin(2 * mp - m)
        - 0.00017 * math.sin(omega)
        - 0.00007 * math.sin(mp + 2 * m)
        + 0.00004 * math.sin(2 * mp - 2 * f)
        + 0.00004 * math.sin(3 * m)
        + 0.00003 * math.sin(mp + m - 2 * f)
        + 0.00003 * math.sin(2 * mp + 2 * f)
        - 0.00003 * math.sin(mp + m + 2 * f)
        + 0.00003 * math.sin(mp - m + 2 * f)
        - 0.00002 * math.sin(mp - m - 2 * f)
        - 0.00002 * math.sin(3 * mp + m)
        + 0.00002 * math.sin(4 * mp)
    )
    return jde + corr


def new_moon_before(jde: float) -> float:
    """返回 jde 之前（含）最近一次朔的 JDE。"""
    k = math.floor(_moon_index(jde))
    result = new_moon_jd(k)
    while result > jde:
        k -= 1
        result = new_moon_jd(k)
    while new_moon_jd(k + 1) <= jde:
        k += 1
        result = new_moon_jd(k)
    return result


def new_moon_after(jde: float) -> float:
    """返回 jde 之后（不含）最近一次朔的 JDE。"""
    k = math.ceil(_moon_index(jde))
    result = new_moon_jd(k)
    while result <= jde:
        k += 1
        result = new_moon_jd(k)
    return result
