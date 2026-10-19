"""法国共和历（French Republican Calendar）。

法国大革命后（1793-1805）短暂使用的十进制历法，是历法史上最激进的一次实验：
- 一年 12 个月，每月固定 30 天，每旬 10 天（废除七曜星期）
- 年末补 5 天（闰年 6 天）「无套裤汉日」（Sans-culottides）
- 每年从秋分开始，元年纪元 An I = 1792-09-22
- 月份按季节风物命名：葡月、雾月、霜月、雪月、雨月、风月、芽月、花月、牧月、
  获月、热月、果月

注：历史上共和历的置闰与秋分实际发生日有过出入，本实现采用 Romme 规则化闰年
（能被 4 整除，除非能被 100 整除但不能被 400 整除），并把葡月 1 日固定为 9-22。
这是最通行的"规则化共和历"口径，适合作为历法换算的玩具。
"""
from __future__ import annotations

from kaleidocal.julian import gregorian_to_jd, jd_to_gregorian

__all__ = [
    "REPUBLICAN_EPOCH_YEAR", "REPUBLICAN_EPOCH_JD",
    "MONTHS", "COMPLEMENTARY_DAYS",
    "republican_to_jd", "jd_to_republican",
]

# 元年 An I 起始 = 1792-09-22（秋分）
REPUBLICAN_EPOCH_YEAR = 1792
REPUBLICAN_EPOCH_JD = gregorian_to_jd(1792, 9, 22)

MONTHS = [
    "Vendémiaire", "Brumaire", "Frimaire", "Nivôse", "Pluviôse", "Ventôse",
    "Germinal", "Floréal", "Prairial", "Messidor", "Thermidor", "Fructidor",
]

MONTHS_CN = [
    "葡月", "雾月", "霜月", "雪月", "雨月", "风月",
    "芽月", "花月", "牧月", "获月", "热月", "果月",
]

COMPLEMENTARY_DAYS = [
    "Vertu（美德日）", "Génie（天才日）", "Travail（劳动日）",
    "Opinion（舆论日）", "Récompenses（奖赏日）", "Révolution（革命日）",
]


def _is_leap_republican(year: int) -> bool:
    """Romme 规则化闰年：能被 4 整除，除非能被 100 整除但不能被 400 整除。"""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _days_in_republican_year(year: int) -> int:
    return 366 if _is_leap_republican(year) else 365


def _republican_year_start_jd(year: int) -> float:
    """共和历 year 年（An year）葡月 1 日的儒略日。"""
    total = 0
    for y in range(1, year):
        total += _days_in_republican_year(y)
    return REPUBLICAN_EPOCH_JD + total


def republican_to_jd(year: int, month: int, day: int) -> float:
    """共和历 (An year, month 1-12, day 1-30) → 儒略日。

    补日（Sans-culottides）用 month=13 表示，day 1-5（闰年 1-6）。
    """
    if not 1 <= month <= 13:
        raise ValueError("month 必须在 1..13（13 表示年末补日）")
    start = _republican_year_start_jd(year)
    days_before = (month - 1) * 30 + (day - 1)
    return start + days_before


def jd_to_republican(jd: float) -> tuple:
    """儒略日 → 共和历 (An year, month, day)。

    month=13 表示年末补日（Sans-culottides），day 为补日序号。
    """
    if jd < REPUBLICAN_EPOCH_JD:
        raise ValueError("该日期早于法国共和历元年（An I）")

    # 逐年代推（共和历只存在了十几年，这里支持任意年份，用于换算趣味）
    year = 1
    while True:
        start = _republican_year_start_jd(year)
        nxt = _republican_year_start_jd(year + 1)
        if start <= jd < nxt:
            break
        year += 1

    offset = int(jd - start)
    month = offset // 30 + 1
    day = offset % 30 + 1
    if month > 12:
        month = 13
        day = offset - 360 + 1
    return year, month, day


def republican_name(month: int, day: int) -> str:
    """把共和历月日转成可读字符串（含补日名）。"""
    if month == 13:
        return COMPLEMENTARY_DAYS[min(day, 6) - 1]
    return f"{MONTHS_CN[month - 1]}（{MONTHS[month - 1]}）{day} 日"
