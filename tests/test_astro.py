"""天文算法（二十四节气）的测试，对拍北京时间日期。"""
from kaleidocal import astro
from kaleidocal.julian import jd_to_gregorian

_CST = 8.0 / 24.0


def _cst_date(jde):
    y, m, d = jd_to_gregorian(jde + _CST)
    return y, m, int(d)


def test_solar_terms_2024():
    """2024 年二分二至的北京时间日期。"""
    expected = {0: (2024, 3, 20), 6: (2024, 6, 21),
                12: (2024, 9, 22), 18: (2024, 12, 21)}
    for k, exp in expected.items():
        assert _cst_date(astro.solar_term_jd(2024, k)) == exp, k


def test_solar_term_monotonic():
    """相邻节气间隔约 14-16 天。

    节气 k18=冬至在 12 月，其后 k19=小寒在次年 1 月，只有这一处跨年。
    """
    for k in range(23):
        if k == 18:
            a = astro.solar_term_jd(2020, 18)
            b = astro.solar_term_jd(2021, 19)
        elif k >= 19:
            a = astro.solar_term_jd(2021, k)
            b = astro.solar_term_jd(2021, k + 1)
        else:
            a = astro.solar_term_jd(2020, k)
            b = astro.solar_term_jd(2020, k + 1)
        assert 13 < b - a < 17, k


def test_winter_solstice_in_december():
    """冬至总在 12 月下旬。"""
    for y in (2019, 2020, 2024, 2030):
        yy, m, d = _cst_date(astro.solar_term_jd(y, 18))
        assert m == 12 and 20 <= d <= 23, (y, m, d)
