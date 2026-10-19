"""儒略日核心与公历互转的测试。"""
import random

from kaleidocal.julian import (
    gregorian_to_jd,
    jd_to_gregorian,
    weekday_index,
    weekday_name,
)


def test_j2000_epoch():
    """J2000.0 基准：2000-01-01 12:00 = JD 2451545.0。"""
    assert gregorian_to_jd(2000, 1, 1) == 2451545.0


def test_known_jd_anchor():
    """1970-01-01 的儒略日为 2440588。"""
    assert int(gregorian_to_jd(1970, 1, 1)) == 2440588


def test_gregorian_to_jd_then_back_roundtrip():
    """公历 → 儒略日 → 公历，应完全还原（随机 2000 组）。"""
    rng = random.Random(0)
    for _ in range(2000):
        y = rng.randint(1, 9999)
        m = rng.randint(1, 12)
        d = rng.randint(1, 28)
        jd = gregorian_to_jd(y, m, d)
        yy, mm, dd = jd_to_gregorian(jd)
        assert (yy, mm, int(dd)) == (y, m, d)


def test_proleptic_julian_calendar_switch():
    """1582-10-04 之前用儒略历，之后用格里历；中间 10 天被跳过。"""
    jd_oct4 = gregorian_to_jd(1582, 10, 4, calendar="julian")
    jd_oct15 = gregorian_to_jd(1582, 10, 15, calendar="gregorian")
    assert jd_oct15 - jd_oct4 == 1.0  # 儒略历 10-04 次日即格里历 10-15


def test_weekday():
    """星期：2024-01-01 是星期一，2000-01-01 是星期六。"""
    assert weekday_index(gregorian_to_jd(2024, 1, 1)) == 1
    assert weekday_name(gregorian_to_jd(2024, 1, 1)) == "一"
    assert weekday_name(gregorian_to_jd(2000, 1, 1)) == "六"
