"""KaleidoCal 命令行入口。

默认（无参数）展示「今天」的综合排盘：同一天在公历、农历、干支、
玛雅历、法国共和历下的样子，直观体会"冷门历法万花筒"。

子命令：
    kaleidocal                        今天综合排盘
    kaleidocal overview 2024-02-10    指定日期的综合排盘
    kaleidocal lunar 2024-02-10       公历 → 农历
    kaleidocal maya  2024-02-10       公历 → 玛雅长纪历 + 历法轮回
    kaleidocal rep   2024-02-10       公历 → 法国共和历
    kaleidocal ganzhi 2024-02-10      干支纪年/日/时
    kaleidocal year 2024              某公历年的农历全览（闰月等）
"""
from __future__ import annotations

import argparse
import datetime
import sys

from kaleidocal import chinese, maya, republican
from kaleidocal import ganzhi
from kaleidocal.julian import gregorian_to_jd, jd_to_gregorian, weekday_name


def _format_calendar_date(y: int, m: int, d: int) -> str:
    """把天文纪年转成可读的公历字符串（含公元前后标注）。"""
    if y <= 0:
        return f"公元前 {-y + 1}年{m}月{d}日"
    return f"{y}年{m}月{d}日"


def _parse_date(date_str: str):
    """解析 YYYY-MM-DD 或 YYYY/M/D，返回 (year, month, day)。"""
    date_str = date_str.replace("/", "-")
    parts = date_str.split("-")
    if len(parts) != 3:
        raise ValueError("日期格式应为 YYYY-MM-DD")
    return int(parts[0]), int(parts[1]), int(parts[2])


def _resolve_date(args):
    """统一解析 date 参数，缺省为今天。"""
    if args.date:
        return _parse_date(args.date)
    now = datetime.date.today()
    return now.year, now.month, now.day


def _overview(year: int, month: int, day: int) -> list:
    """生成某公历日期的综合排盘文本行。"""
    jd = gregorian_to_jd(year, month, day)
    jdn = int(jd)
    lines = []
    lines.append(f"公历       {_format_calendar_date(year, month, day)}（星期{weekday_name(jd)}）")
    lines.append(f"儒略日     JDN {jdn}")

    # 农历
    lunar = chinese.gregorian_to_lunar(year, month, day)
    lines.append(
        f"农历       {lunar['ganzhi_year']}年（{lunar['zodiac']}年）"
        f"{lunar['month_name']}{lunar['day']}日"
    )

    # 干支
    lines.append(
        f"干支       {lunar['ganzhi_year']}年"
        f" 日柱 {ganzhi.day_ganzhi(year, month, day)}"
    )

    # 玛雅
    b, k, t, u, kin = maya.jdn_to_maya(jdn)
    lines.append(
        f"玛雅长纪历 {b}.{k}.{t}.{u}.{kin}"
        f"  历法轮回：{maya.calendar_round(jdn)}"
    )

    # 共和历
    ryear, rmonth, rday = republican.jd_to_republican(jd)
    lines.append(f"法国共和历 An {ryear} {republican.republican_name(rmonth, rday)}")

    return lines


def cmd_overview(args) -> int:
    if args.date:
        year, month, day = _parse_date(args.date)
    else:
        now = datetime.date.today()
        year, month, day = now.year, now.month, now.day
    for line in _overview(year, month, day):
        print(line)
    return 0


def cmd_lunar(args) -> int:
    y, m, d = _resolve_date(args)
    info = chinese.gregorian_to_lunar(y, m, d)
    print(f"{_format_calendar_date(y, m, d)} → 农历：")
    print(f"  {info['ganzhi_year']}年（{info['zodiac']}年）{info['month_name']}{info['day']}日")
    return 0


def cmd_maya(args) -> int:
    y, m, d = _resolve_date(args)
    jdn = int(gregorian_to_jd(y, m, d))
    b, k, t, u, kin = maya.jdn_to_maya(jdn)
    print(f"{_format_calendar_date(y, m, d)} → 玛雅历：")
    print(f"  长纪历   {b}.{k}.{t}.{u}.{kin}")
    print(f"  历法轮回 {maya.calendar_round(jdn)}")
    return 0


def cmd_rep(args) -> int:
    y, m, d = _resolve_date(args)
    jd = gregorian_to_jd(y, m, d)
    ryear, rmonth, rday = republican.jd_to_republican(jd)
    print(f"{_format_calendar_date(y, m, d)} → 法国共和历：")
    print(f"  An {ryear} {republican.republican_name(rmonth, rday)}")
    return 0


def cmd_ganzhi(args) -> int:
    y, m, d = _resolve_date(args)
    print(f"{_format_calendar_date(y, m, d)} 的干支：")
    print(f"  纪年 {ganzhi.year_ganzhi(y)}（{ganzhi.zodiac_of_year(y)}年）")
    print(f"  纪日 {ganzhi.day_ganzhi(y, m, d)}")
    for h in (0, 6, 12, 18):
        print(f"  纪时 {h:02d}:00 → {ganzhi.hour_ganzhi(y, m, d, h)}")
    return 0


def cmd_year(args) -> int:
    info = chinese.lunar_year_info(args.year)
    print(f"公历 {args.year} 年对应的农历年：")
    print(f"  干支：{info['ganzhi_year']}年（{info['zodiac']}年）")
    y, m, d = info["lunar_new_year"]
    print(f"  春节：{_format_calendar_date(y, m, d)}")
    print(f"  共 {info['month_count']} 个月")
    if info["leap_months"]:
        for lm, ld in info["leap_months"]:
            name = chinese.LUNAR_MONTH_NAMES[lm]
            print(f"  闰月：闰{name}（{ld} 天）")
    else:
        print("  闰月：无")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kaleidocal",
        description="冷门历法万花筒：农历 / 干支 / 玛雅历 / 法国共和历 任意互转",
    )
    sub = p.add_subparsers(dest="command")

    sp = sub.add_parser("overview", help="某日综合排盘（默认命令）")
    sp.add_argument("date", nargs="?", help="YYYY-MM-DD，缺省为今天")
    sp.set_defaults(func=cmd_overview)

    sp = sub.add_parser("lunar", help="公历 → 农历")
    sp.add_argument("date", nargs="?", help="YYYY-MM-DD")
    sp.set_defaults(func=cmd_lunar)

    sp = sub.add_parser("maya", help="公历 → 玛雅历")
    sp.add_argument("date", nargs="?", help="YYYY-MM-DD")
    sp.set_defaults(func=cmd_maya)

    sp = sub.add_parser("rep", help="公历 → 法国共和历")
    sp.add_argument("date", nargs="?", help="YYYY-MM-DD")
    sp.set_defaults(func=cmd_rep)

    sp = sub.add_parser("ganzhi", help="干支纪年/日/时")
    sp.add_argument("date", nargs="?", help="YYYY-MM-DD")
    sp.set_defaults(func=cmd_ganzhi)

    sp = sub.add_parser("year", help="某公历年的农历全览")
    sp.add_argument("year", type=int)
    sp.set_defaults(func=cmd_year)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        # 无子命令 → 今天综合排盘
        args.date = getattr(args, "date", None)
        return cmd_overview(args)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
