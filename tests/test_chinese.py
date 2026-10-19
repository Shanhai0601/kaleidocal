"""农历（定气定朔）的测试，与权威万年历数据对拍。"""
from kaleidocal import chinese


def test_lunar_new_year_dates():
    """春节日期对拍（权威数据）。"""
    expected = {
        2020: (2020, 1, 25),
        2023: (2023, 1, 22),
        2024: (2024, 2, 10),
        2025: (2025, 1, 29),
        2026: (2026, 2, 17),
        2028: (2028, 1, 26),
    }
    for y, exp in expected.items():
        assert chinese.lunar_year_info(y)["lunar_new_year"] == exp, y


def test_leap_months():
    """闰月对拍（权威数据）。"""
    expected = {2020: 4, 2023: 2, 2024: None, 2025: 6, 2028: 5}
    for y, exp in expected.items():
        leaps = chinese.lunar_year_info(y)["leap_months"]
        actual = leaps[0][0] if leaps else None
        assert actual == exp, (y, leaps)


def test_gregorian_to_lunar_samples():
    """具体日期转农历（权威数据）。"""
    samples = [
        (2023, 1, 22, "癸卯", "正月", 1, False),
        (2023, 3, 22, "癸卯", "闰二月", 1, True),
        (2024, 2, 10, "甲辰", "正月", 1, False),
        (2025, 1, 28, "甲辰", "腊月", 29, False),  # 除夕（小月廿九）
        (2025, 7, 25, "乙巳", "闰六月", 1, True),
        (2025, 8, 23, "乙巳", "七月", 1, False),   # 闰六月之后接七月
        (2026, 2, 17, "丙午", "正月", 1, False),
    ]
    for y, m, d, gy, mn, dd, leap in samples:
        r = chinese.gregorian_to_lunar(y, m, d)
        assert r["ganzhi_year"] == gy, (y, m, d, r)
        assert r["month_name"] == mn, (y, m, d, r)
        assert r["day"] == dd, (y, m, d, r)
        assert r["leap"] == leap, (y, m, d, r)


def test_year_boundary():
    """春节前仍属上一个农历年。"""
    # 2025-01-28（除夕）仍属甲辰年，2025-01-29（春节）起属乙巳年
    assert chinese.gregorian_to_lunar(2025, 1, 28)["ganzhi_year"] == "甲辰"
    assert chinese.gregorian_to_lunar(2025, 1, 29)["ganzhi_year"] == "乙巳"
