"""KaleidoCal —— 冷门历法万花筒。

把农历、干支、玛雅长纪历、法国共和历等平时没人用的历法，
统一到「儒略日」这个天文时间尺度上，实现任意两种历法的互转。

用法：
    from kaleidocal import chinese, maya, republican
    from kaleidocal.julian import gregorian_to_jd, jd_to_gregorian
"""

__version__ = "0.1.0"
__all__ = ["julian", "astro", "ganzhi", "maya", "republican", "chinese"]
