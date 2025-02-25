import logging
import os
from abc import ABCMeta
from importlib.resources import read_text
from pathlib import Path

from virtualenv.info import fs_supports_symlink

from ..creator import Creator, CreatorMeta


class ViaGlobalRefMeta(CreatorMeta):
    def __init__(self):
        super().__init__()
        self.copy_error = None
        self.symlink_error = None
        if not fs_supports_symlink():
            self.symlink_error = "the filesystem does not supports symlink"

    @property
    def can_copy(self):
        return not self.copy_error

    @property
    def can_symlink(self):
        return not self.symlink_error


class ViaGlobalRefApi(Creator, metaclass=ABCMeta):
    def __init__(self, options, interpreter):
        super().__init__(options, interpreter)
        self.symlinks = self._should_symlink(options)
        self.enable_system_site_package = options.system_site

    @staticmethod
    def _should_symlink(options):
        # Priority of where the option is set to follow the order: CLI, env var, file, hardcoded.
        # If both set at same level prefers copy over symlink.
        copies, symlinks = getattr(options, "copies", False), getattr(options, "symlinks", False)
        copy_src, sym_src = options.get_source("copies"), options.get_source("symlinks")
        for level in ["cli", "env var", "file", "default"]:
            s_opt = symlinks if sym_src == level else None
            c_opt = copies if copy_src == level else None
            if s_opt is True and c_opt is True:
                return False
            if s_opt is True:
                return True
            if c_opt is True:
                return False
        return False  # fallback to copy

    @classmethod
    def add_parser_arguments(cls, parser, interpreter, meta, app_data):
        super().add_parser_arguments(parser, interpreter, meta, app_data)
        parser.add_argument(
            "--system-site-packages",
            default=False,
            action="store_true",
            dest="system_site",
            help="give the virtual environment access to the system site-packages dir",
        )
        group = parser.add_mutually_exclusive_group()
        if not meta.can_symlink and not meta.can_copy:
            raise RuntimeError("neither symlink or copy method supported")
        if meta.can_symlink:
            group.add_argument(
                "--symlinks",
                default=True,
                action="store_true",
                dest="symlinks",
                help="try to use symlinks rather than copies, when symlinks are not the default for the platform",
            )
        if meta.can_copy:
            group.add_argument(
                "--copies",
                "--always-copy",
                default=not meta.can_symlink,
                action="store_true",
                dest="copies",
                help="try to use copies rather than symlinks, even when symlinks are the default for the platform",
            )

    def create(self):
        self.install_patch()

    def install_patch(self):
        text = self.env_patch_text()
        if text:
            pth = self.purelib / "_virtualenv.pth"
            logging.debug("create virtualenv import hook file %s", pth)
            pth.write_text("import _virtualenv")
            dest_path = self.purelib / "_virtualenv.py"
            logging.debug("create %s", dest_path)
            dest_path.write_text(text)

    def env_patch_text(self):
        """Patch the distutils package to not be derailed by its configuration files"""
        from . import __name__
        text = read_text(__name__, "_virtualenv.py.template")
        return text.replace('"__SCRIPT_DIR__"', repr(os.path.relpath(str(self.script_dir), str(self.purelib))))

    def _args(self):
        return super()._args() + [("global", self.enable_system_site_package)]

    def set_pyenv_cfg(self):
        super().set_pyenv_cfg()
        self.pyenv_cfg["include-system-site-packages"] = "true" if self.enable_system_site_package else "false"


__all__ = [
    "ViaGlobalRefMeta",
    "ViaGlobalRefApi",
]
