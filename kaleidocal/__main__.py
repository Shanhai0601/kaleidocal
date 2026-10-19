"""支持 `python -m kaleidocal` 直接运行。"""
import sys

from kaleidocal.cli import main

if __name__ == "__main__":
    sys.exit(main())
