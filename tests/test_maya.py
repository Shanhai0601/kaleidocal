"""玛雅长纪历、卓尔金历、哈布历的测试。"""
from kaleidocal import maya
from kaleidocal.julian import gregorian_to_jd


def test_epoch_is_4_ahau_8_cumku():
    """纪元 0.0.0.0.0 = JDN 584283 = 4 Ahau 8 Cumku。"""
    assert maya.tzolkin(584283) == (4, "Ahau")
    assert maya.haab(584283) == (8, "Cumku")


def test_2012_end_of_long_count():
    """2012-12-21 = 长纪历 13.0.0.0.0 = 4 Ahau 3 Kankin（著名"世界末日"）。"""
    jdn = int(gregorian_to_jd(2012, 12, 21))
    assert maya.jdn_to_maya(jdn) == (13, 0, 0, 0, 0)
    assert maya.tzolkin(jdn) == (4, "Ahau")
    assert maya.haab(jdn) == (3, "Kankin")
    assert maya.calendar_round(jdn) == "4 Ahau / 3 Kankin"


def test_maya_roundtrip():
    """长纪历 → 儒略日 → 长纪历，应还原。

    注意：长纪历 uinal 位是 18 进制（18 uinal = 1 tun），kin < 20，
    故用例须取规范值（uinal < 18）。
    """
    for lc in [(0, 0, 0, 0, 0), (13, 0, 0, 0, 0), (12, 19, 17, 16, 19), (9, 8, 7, 6, 5)]:
        jdn = maya.maya_to_jdn(*lc)
        assert maya.jdn_to_maya(jdn) == lc


def test_pre_epoch_raises():
    """早于纪元的长纪历换算应报错。"""
    import pytest
    with pytest.raises(ValueError):
        maya.jdn_to_maya(584283 - 1)
