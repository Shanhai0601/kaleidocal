"""CLI 入口测试：各子命令应能正常解析并输出，退出码为 0。"""
from kaleidocal.cli import main


def test_overview_subcommand(capsys):
    assert main(["overview", "2012-12-21"]) == 0
    out = capsys.readouterr().out
    assert "玛雅长纪历 13.0.0.0.0" in out
    assert "儒略日" in out


def test_lunar_subcommand(capsys):
    assert main(["lunar", "2025-07-25"]) == 0
    out = capsys.readouterr().out
    assert "闰六月" in out


def test_maya_subcommand(capsys):
    assert main(["maya", "1997-08-29"]) == 0
    assert "长纪历" in capsys.readouterr().out


def test_rep_subcommand(capsys):
    assert main(["rep", "1794-07-27"]) == 0
    assert "热月" in capsys.readouterr().out


def test_ganzhi_subcommand(capsys):
    assert main(["ganzhi", "2024-01-01"]) == 0
    assert "纪日" in capsys.readouterr().out


def test_year_subcommand(capsys):
    assert main(["year", "2025"]) == 0
    assert "闰六月" in capsys.readouterr().out


def test_default_no_args(capsys):
    """无子命令时应回退到「今天综合排盘」且不崩溃。"""
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "儒略日" in out
    assert "玛雅长纪历" in out
