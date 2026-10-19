"""中国农历（夏历/阴阳历）—— 定气定朔法。

农历是最精巧的一类历法：它同时调和太阳（节气）与月亮（朔望）两个周期。
- 以「朔」（日月黄经相合）为每月初一，故大月 30 天、小月 29 天
- 以「中气」（太阳视黄经 30° 的整数倍）定月名，冬至所在月必为十一月
- 若某月不含任何中气，则为闰月，闰它前一个月
- 正月初一（春节）= 前一年冬至后的第二个朔

全部由 astro 模块的天文算法实时计算，不依赖任何万年历数据表。

**时区约定（关键）**：朔与中气是天文学「时刻」（世界时 UT），但农历的
月、日、闰月归属都按「北京时间（UTC+8）的哪一天」判定。因此所有月边界
与中气归属都先 +8 小时换算成北京时间的公历日期，再做区间比较——否则朔
落在 20:00~24:00 世界时（即北京次日凌晨）时，会出现整月错位一天、
闰月错移一位的错误。
"""
from __future__ import annotations

import math
from functools import lru_cache

from kaleidocal import astro
from kaleidocal.julian import gregorian_to_jd, jd_to_gregorian
from kaleidocal.ganzhi import year_ganzhi, zodiac_of_year

__all__ = [
    "LUNAR_MONTH_NAMES",
    "lunar_new_year_jd", "build_lunar_year",
    "gregorian_to_lunar", "lunar_year_info",
]

LUNAR_MONTH_NAMES = [
    "", "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "腊月",
]

_SYNODIC = 29.530588861
_MOON_EPOCH = 2451550.09766
_CST = 8.0 / 24.0  # 北京时间 = UTC+8


def _moon_k(jde: float) -> int:
    """给定 JDE，返回月相编号 k 的整数估计。"""
    return math.floor((jde - _MOON_EPOCH) / _SYNODIC)


def _winter_solstice_jd(year: int) -> float:
    """公历 year 年的冬至 JDE（黄经 270° = k18）。"""
    return astro.solar_term_jd(year, 18)


def _cst_date(jde: float):
    """把世界时时刻 JDE 换算成北京时间下的公历日期 (y, m, d)。"""
    y, m, d = jd_to_gregorian(jde + _CST)
    return y, m, int(d)


def _ymd_to_jdn(y: int, m: int, d: int) -> int:
    """公历日期 → 儒略日整数 JDN。"""
    return int(gregorian_to_jd(y, m, d))


@lru_cache(maxsize=256)
def lunar_new_year_jd(year: int) -> float:
    """公历 year 年的春节（农历正月初一）所对应的朔 JDE。

    正月初一 = 冬至后第二个朔。这里的冬至是「前一年」的冬至：
    农历年 year 的春节落在公历 year 年 1/2 月，其定月所依据的冬至
    发生在公历 (year-1) 年 12 月。
    """
    ws = _winter_solstice_jd(year - 1)
    k = _moon_k(ws)
    while astro.new_moon_jd(k) <= ws:
        k += 1
    return astro.new_moon_jd(k + 1)


def _major_term_in_cst(start_jdn: int, end_jdn: int):
    """判断 [start_jdn, end_jdn)（北京时间日）内包含哪个中气。

    返回中气序号 0-11（对应 astro.MAJOR_TERMS），无中气则返回 None。
    中气间隔约 30.4 天，大于月长（29-30 天），故一月最多含一个中气。
    """
    y, _, _ = jd_to_gregorian(start_jdn)
    for yy in (y - 1, y, y + 1):
        for k in range(0, 24, 2):  # 0,2,...,22 为中气
            tj_jdn = _ymd_to_jdn(*_cst_date(astro.solar_term_jd(yy, k)))
            if start_jdn <= tj_jdn < end_jdn:
                return k // 2
    return None


@lru_cache(maxsize=256)
def build_lunar_year(year: int) -> tuple:
    """构建公历 year 年（春节所在年）对应的农历年月份表。

    返回 tuple[dict]，每项含：
        start:     本月初一对应的朔 JDE
        next:      下月初一对应的朔 JDE
        start_jdn: 本月初一在北京时间的儒略日整数
        next_jdn:  下月初一在北京时间的儒略日整数
        days:      本月天数（29/30）
        month:     月号 1-12
        leap:      是否闰月
    """
    start_jde = lunar_new_year_jd(year)
    end_jde = lunar_new_year_jd(year + 1)

    # 收集本农历年内所有朔（含正月初一，不含下一年正月初一）
    moons = []
    k = _moon_k(start_jde)
    jde = astro.new_moon_jd(k)
    while jde < start_jde:
        k += 1
        jde = astro.new_moon_jd(k)
    while jde < end_jde - 1e-6:
        moons.append(jde)
        k += 1
        jde = astro.new_moon_jd(k)

    # 每个朔的北京时间初一日期及其儒略日整数
    start_dates = [_cst_date(m) for m in moons]
    start_jdns = [_ymd_to_jdn(*d) for d in start_dates]
    end_jdn = _ymd_to_jdn(*_cst_date(end_jde))
    start_jdns.append(end_jdn)  # 最后一个月的下月初一

    result = []
    for i, s_jde in enumerate(moons):
        this_jdn = start_jdns[i]
        next_jdn = start_jdns[i + 1]
        days = next_jdn - this_jdn
        major = _major_term_in_cst(this_jdn, next_jdn)
        next_jde = moons[i + 1] if i + 1 < len(moons) else end_jde
        if major is None:
            # 无中气 → 闰月，闰前一个月
            prev = result[-1]
            result.append({
                "start": s_jde, "next": next_jde,
                "start_jdn": this_jdn, "next_jdn": next_jdn,
                "days": days, "month": prev["month"], "leap": True,
            })
        else:
            num = (major + 2) % 12
            result.append({
                "start": s_jde, "next": next_jde,
                "start_jdn": this_jdn, "next_jdn": next_jdn,
                "days": days, "month": 12 if num == 0 else num, "leap": False,
            })
    return tuple(result)


def gregorian_to_lunar(year: int, month: int, day: int) -> dict:
    """公历日期 → 农历信息。

    返回 dict：{year, month, day, leap, days, ganzhi_year, zodiac, month_name}。
    """
    jdn = _ymd_to_jdn(year, month, day)
    lny_jdn = _ymd_to_jdn(*_cst_date(lunar_new_year_jd(year)))
    lunar_year = year if jdn >= lny_jdn else year - 1

    months = build_lunar_year(lunar_year)
    for m in months:
        if m["start_jdn"] <= jdn < m["next_jdn"]:
            day_num = jdn - m["start_jdn"] + 1
            month_name = LUNAR_MONTH_NAMES[m["month"]]
            if m["leap"]:
                month_name = "闰" + month_name
            return {
                "year": lunar_year,
                "month": m["month"],
                "day": day_num,
                "leap": m["leap"],
                "days": m["days"],
                "ganzhi_year": year_ganzhi(lunar_year),
                "zodiac": zodiac_of_year(lunar_year),
                "month_name": month_name,
            }
    raise ValueError(f"无法定位农历日期：{year}-{month}-{day}")


def lunar_year_info(year: int) -> dict:
    """返回公历 year 年对应农历年的概览（闰月、各月天数、春节日期）。"""
    months = build_lunar_year(year)
    lny = _cst_date(lunar_new_year_jd(year))
    leaps = [x for x in months if x["leap"]]
    return {
        "ganzhi_year": year_ganzhi(year),
        "zodiac": zodiac_of_year(year),
        "lunar_new_year": lny,
        "month_count": len(months),
        "leap_months": [(x["month"], x["days"]) for x in leaps],
        "months": [(x["month"], x["days"], x["leap"]) for x in months],
    }
