from __future__ import absolute_import, unicode_literals

from pathlib import Path

from virtualenv import __path_assets__

_PATH_ASSETS = (
    __path_assets__ / "discovery" if __path_assets__ else
    Path(__path__[0])
)
