"""天干地支（干支）与生肖。

干支纪法以 60 为一个周期（六十甲子），是中国传统历法的时间坐标：
- 干支纪年：以立春（或正月初一）为界，公元 4 年为甲子年
- 干支纪日：连续不断，以儒略日为基准（2019-01-27 为甲子日）
- 干支纪时：十二时辰 + 五鼠遁时法

参考基准已与「ChineseCalendar」历法库交叉验证：
  天干 = (JDN + 9) % 10，地支 = (JDN + 1) % 12，六十甲子序号 = (JDN + 49) % 60。
"""
from __future__ import annotations

import math

from kaleidocal.julian import gregorian_to_jd

__all__ = [
    "GAN", "ZHI", "SHENGXIAO",
    "year_ganzhi", "day_ganzhi", "hour_ganzhi",
    "zodiac_of_year",
]

GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
SHENGXIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]


def year_ganzhi(year: int) -> str:
    """公历年 → 干支纪年（以立春/正月初一为界，这里约定以农历正月初一为界）。

    公元 4 年为甲子年，故 (year - 4) 对 10、12 取模。
    """
    g = (year - 4) % 10
    z = (year - 4) % 12
    return GAN[g] + ZHI[z]


def zodiac_of_year(year: int) -> str:
    """公历年 → 生肖（与干支纪年地支同源）。"""
    return SHENGXIAO[(year - 4) % 12]


def day_ganzhi(year: int, month: int, day: int) -> str:
    """公历日期 → 干支纪日（六十甲子）。

    日干支以儒略日 JDN 为基准，公式经「2019-01-27 = 甲子日」锚点验证。
    """
    jdn = int(gregorian_to_jd(year, month, day))
    g = (jdn + 9) % 10
    z = (jdn + 1) % 12
    return GAN[g] + ZHI[z]


def _day_gan_index(year: int, month: int, day: int) -> int:
    """公历日期 → 日天干序号（0-9），供五鼠遁时法使用。"""
    jdn = int(gregorian_to_jd(year, month, day))
    return (jdn + 9) % 10


def hour_ganzhi(year: int, month: int, day: int, hour: int) -> str:
    """公历日期 + 小时 → 干支纪时（十二时辰）。

    时辰：23-01 子、01-03 丑……21-23 亥。
    时干用五鼠遁时法：由日干推出子时天干，再逐时辰顺推。
    """
    # 十二时辰地支，索引 0=子时（23:00-01:00）
    if hour == 23:
        branch_idx = 0  # 23:00 起属子时
    else:
        branch_idx = (hour + 1) // 2 % 12  # 0=子(23,0,1), 1=丑(1,3)...

    # 五鼠遁：子时天干由日干决定
    day_gan = _day_gan_index(year, month, day)
    # 甲己→甲子, 乙庚→丙子, 丙辛→戊子, 丁壬→庚子, 戊癸→壬子
    start_gan = ((day_gan % 5) * 2) % 10
    gan_idx = (start_gan + branch_idx) % 10
    return GAN[gan_idx] + ZHI[branch_idx]
