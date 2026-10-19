"""干支与生肖的测试。"""
from kaleidocal import ganzhi


def test_year_ganzhi_anchor():
    """公元 4 年为甲子年。"""
    assert ganzhi.year_ganzhi(4) == "甲子"
    assert ganzhi.year_ganzhi(1984) == "甲子"  # 1984 = 4 + 60×33
    assert ganzhi.year_ganzhi(2024) == "甲辰"
    assert ganzhi.year_ganzhi(2025) == "乙巳"


def test_zodiac():
    assert ganzhi.zodiac_of_year(2024) == "龙"
    assert ganzhi.zodiac_of_year(1984) == "鼠"


def test_day_ganzhi_anchor():
    """2019-01-27 为甲子日（公认锚点）。"""
    assert ganzhi.day_ganzhi(2019, 1, 27) == "甲子"


def test_day_ganzhi_60_cycle():
    """干支纪日 60 天一循环。"""
    a = ganzhi.day_ganzhi(2024, 1, 1)
    b = ganzhi.day_ganzhi(2024, 3, 1)  # 相差 60 天
    assert a == b
    assert ganzhi.day_ganzhi(2024, 1, 2) != a


def test_hour_ganzhi_five_mouse():
    """五鼠遁：甲己日子时起甲子。2024-01-01 为甲子日。"""
    assert ganzhi.hour_ganzhi(2024, 1, 1, 23) == "甲子"  # 子时
    assert ganzhi.hour_ganzhi(2024, 1, 1, 6) == "丁卯"   # 卯时
    assert ganzhi.hour_ganzhi(2024, 1, 1, 12) == "庚午"  # 午时
