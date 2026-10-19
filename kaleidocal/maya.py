"""玛雅历：长纪历（Long Count）、卓尔金历（Tzolk'in）、哈布历（Haab）。

玛雅文明最精妙的是同时并行多套历法：
- 长纪历：从神话纪元起算的连续天数，用 5 个位置计数（baktun.katun.tun.uinal.kin）
- 卓尔金历：260 天（13 个数字 × 20 个日名），用于宗教仪式
- 哈布历：365 天（18 个月 × 20 天 + 5 天 Wayeb），近似太阳年

三套历法组合成 52 年的"历法轮回"（Calendar Round）。

纪元相关（GMT correlation，最广泛接受的关联常数）：
长纪历 0.0.0.0.0 = JDN 584283 = 公历 3114-08-11（格里历 proleptic）。
由此可推出 2012-12-21（JDN 2456283）= 13.0.0.0.0 —— 著名的"2012 世界末日"。
"""
from __future__ import annotations

from kaleidocal.julian import jd_to_gregorian

__all__ = [
    "MAYA_EPOCH_JDN",
    "maya_to_jdn", "jdn_to_maya",
    "tzolkin", "haab", "calendar_round",
    "TZOLKIN_NAMES", "HAAB_MONTHS",
]

# 长纪历纪元（GMT 584283）：0.0.0.0.0 对应的儒略日整数
MAYA_EPOCH_JDN = 584283

# 卓尔金历 20 个日名
TZOLKIN_NAMES = [
    "Imix", "Ik", "Akbal", "Kan", "Chicchan", "Cimi", "Manik",
    "Lamat", "Muluc", "Oc", "Chuen", "Eb", "Ben", "Ix", "Men",
    "Cib", "Caban", "Etznab", "Cauac", "Ahau",
]

# 哈布历 18 个月 + 5 天 Wayeb
HAAB_MONTHS = [
    "Pop", "Wo", "Sip", "Sotz", "Sek", "Xul",
    "Yaxkin", "Mol", "Chen", "Yax", "Zac", "Ceh",
    "Mac", "Kankin", "Muan", "Pax", "Kayab", "Cumku",
]


def _long_count_to_days(baktun: int, katun: int, tun: int, uinal: int, kin: int) -> int:
    """长纪历五个位置 → 自纪元起的天数。"""
    return kin + 20 * uinal + 360 * tun + 7200 * katun + 144000 * baktun


def maya_to_jdn(baktun: int, katun: int, tun: int, uinal: int, kin: int) -> int:
    """长纪历 → 儒略日整数 JDN。"""
    days = _long_count_to_days(baktun, katun, tun, uinal, kin)
    return MAYA_EPOCH_JDN + days


def jdn_to_maya(jdn: int) -> tuple:
    """儒略日整数 JDN → 长纪历 (baktun, katun, tun, uinal, kin)。"""
    n = jdn - MAYA_EPOCH_JDN
    if n < 0:
        raise ValueError("该儒略日早于玛雅长纪历纪元（0.0.0.0.0）")
    baktun, n = divmod(n, 144000)
    katun, n = divmod(n, 7200)
    tun, n = divmod(n, 360)
    uinal, kin = divmod(n, 20)
    return baktun, katun, tun, uinal, kin


# 卓尔金历在纪元日的相位：0.0.0.0.0 = 4 Ahau（数字 4，日名 Ahau=索引 19）。
# 由 CRT 解 p≡3(mod13) 且 p≡19(mod20) 得循环相位 p=159。
_TZOLKIN_EPOCH_OFFSET = 159


def tzolkin(jdn: int) -> tuple:
    """儒略日整数 JDN → 卓尔金历 (数字 1-13, 日名)。

    卓尔金历从纪元起每 260 天循环一次；纪元日相位为 4 Ahau。
    """
    offset = (jdn - MAYA_EPOCH_JDN + _TZOLKIN_EPOCH_OFFSET) % 260
    number = (offset % 13) + 1
    name_idx = offset % 20
    return number, TZOLKIN_NAMES[name_idx]


def haab(jdn: int) -> tuple:
    """儒略日整数 JDN → 哈布历 (月内日 0-19, 月名)。

    哈布历从纪元起每 365 天循环，年末的 5 天 Wayeb 不属于任何月。
    纪元当日对应 8 Cumku（历史关联常识），故加 348 天偏移对齐。
    """
    offset = (jdn - MAYA_EPOCH_JDN + 348) % 365
    if offset < 360:
        month_idx = offset // 20
        day = offset % 20
        return day, HAAB_MONTHS[month_idx]
    return offset - 360, "Wayeb"


def calendar_round(jdn: int) -> str:
    """儒略日整数 JDN → 历法轮回字符串（Tzolk'in + Haab 组合）。"""
    number, name = tzolkin(jdn)
    day, month = haab(jdn)
    return f"{number} {name} / {day} {month}"


def maya_date_verbose(baktun, katun, tun, uinal, kin):
    """把长纪历五个数格式化为可读字符串。"""
    return f"{baktun}.{katun}.{tun}.{uinal}.{kin}"
