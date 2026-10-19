# KaleidoCal · 冷门历法万花筒

> 同一个日子，在不同文明眼里，是完全不同的时间坐标。

输入一个公历日期，KaleidoCal 会告诉你这一天在**农历**、**干支**、**玛雅历**、**法国共和历**下分别是什么样子——就像透过万花筒，看到同一个事实折射出的多种文明想象。

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![tests](https://img.shields.io/badge/tests-32%20passed-brightgreen.svg)](./tests)

## 快速开始

```bash
pip install -e .          # 安装到当前环境（或直接 python -m kaleidocal）

kaleidocal                          # 今天的综合排盘
kaleidocal overview 2012-12-21      # 指定日期的综合排盘
kaleidocal lunar 2025-07-25         # 公历 → 农历
kaleidocal maya  1997-08-29         # 公历 → 玛雅长纪历 + 历法轮回
kaleidocal rep   1794-07-27         # 公历 → 法国共和历
kaleidocal ganzhi 2024-01-01        # 干支纪年/日/时
kaleidocal year 2025                # 某公历年的农历全览（闰月等）
```

不装包也可直接用 `python -m kaleidocal overview 2012-12-21`。

### 效果示例

```
$ python -m kaleidocal overview 2012-12-21
公历       2012年12月21日（星期五）
儒略日     JDN 2456283
农历       壬辰年（龙年）冬月9日
干支       壬辰年 日柱 壬寅
玛雅长纪历 13.0.0.0.0  历法轮回：4 Ahau / 3 Kankin
法国共和历 An 221 雪月（Nivôse）1 日
```

> 2012-12-21 正是玛雅长纪历第 13 个 baktun 结束的日子，被误传为「世界末日」；在 KaleidoCal 里，它只是四套历法里一个普通但可以精确交叉验证的坐标。

## 支持哪些历法

| 历法 | 类型 | 关键规则 |
| --- | --- | --- |
| 公历（格里历/儒略历） | 太阳历 | 1582-10-15 起用格里历，之前用儒略历 |
| 农历（夏历） | 阴阳历 | 定气定朔；正月初一 = 前一年冬至后第二个朔；无中气置闰 |
| 干支（天干地支） | 六十甲子 | 纪年以公元 4 年为甲子；纪日以儒略日为基准 |
| 玛雅历 | 多套并行 | 长纪历 + 卓尔金历（260 天）+ 哈布历（365 天）+ 52 年历法轮回 |
| 法国共和历 | 太阳历 | 一年 12 月 × 30 天 + 年末 5~6 天补日，从 1792-09-22 秋分起算 |

## 设计亮点

- **以儒略日（JD）为"中间货币"**：任一历法先转 JD，再由 JD 转目标历法，使 N 种历法的互转只需 N 个转换器，而非 N² 个两两转换。
- **纯算法、零数据表**：农历的节气与朔、玛雅历、共和历全部由天文公式实时推算，不内置任何万年历查表。太阳视黄经与朔望月基于 Jean Meeus《Astronomical Algorithms》，精度约 ±1 分钟。
- **正确处理时区**：农历的月、日、闰月归属按**北京时间（UTC+8）的日**判定，而非世界时时刻——这是农历排盘中极易踩坑的一处细节。
- **可交叉验证**：每个模块都有独立的已知历表锚点测试（如 2012-12-21 = 13.0.0.0.0、2019-01-27 = 甲子日、1794-07-27 = 热月政变）。

## 目录结构

```
kaleidocal/
├── kaleidocal/
│   ├── __init__.py     # 包初始化与版本号
│   ├── __main__.py     # python -m kaleidocal 入口
│   ├── julian.py       # 儒略日核心（所有历法的中间货币）
│   ├── astro.py        # 天文算法：太阳视黄经（节气）、朔（月相）
│   ├── ganzhi.py       # 干支纪年/日/时与生肖
│   ├── chinese.py      # 农历（定气定朔、闰月、春节）
│   ├── maya.py         # 玛雅长纪历 / 卓尔金历 / 哈布历 / 历法轮回
│   ├── republican.py   # 法国共和历
│   └── cli.py          # 命令行入口
├── tests/              # pytest 测试（32 个用例，含历表锚点对拍）
├── docs/               # 需求文档、技术方案
├── pyproject.toml
└── LICENSE
```

## 运行测试

```bash
pip install pytest
python -m pytest -q
```

## 许可

[MIT](./LICENSE)
