"""法国共和历的测试。"""
from kaleidocal import republican
from kaleidocal.julian import gregorian_to_jd


def test_epoch():
    """元年纪元 An I 葡月 1 日 = 1792-09-22。"""
    jd = gregorian_to_jd(1792, 9, 22)
    assert republican.jd_to_republican(jd) == (1, 1, 1)
    assert republican.republican_to_jd(1, 1, 1) == jd


def test_thermidor_coup():
    """热月政变 1794-07-27 = An II 热月（Thermidor）9 日。"""
    jd = gregorian_to_jd(1794, 7, 27)
    year, month, day = republican.jd_to_republican(jd)
    assert (year, month, day) == (2, 11, 9)
    assert "热月" in republican.republican_name(month, day)


def test_roundtrip():
    """共和历 → 儒略日 → 共和历，应还原。"""
    for y, m, d in [(1, 1, 1), (2, 11, 9), (14, 13, 5), (3, 7, 30)]:
        jd = republican.republican_to_jd(y, m, d)
        assert republican.jd_to_republican(jd) == (y, m, d)


def test_complementary_days():
    """年末补日（Sans-culottides）用 month=13 表示。"""
    # An I 是平年，补日 5 天，第 361 天起
    jd = republican.republican_to_jd(1, 13, 1)
    y, m, d = republican.jd_to_republican(jd)
    assert (y, m, d) == (1, 13, 1)
    assert "美德" in republican.republican_name(13, 1)
