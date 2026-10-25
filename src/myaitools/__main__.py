"""支持 ``python -m myaitools`` 的运行方式。"""

from __future__ import annotations

import sys

from myaitools.cli import main

if __name__ == "__main__":
    sys.exit(main())
