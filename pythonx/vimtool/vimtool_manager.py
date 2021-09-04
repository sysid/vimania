import logging
import tempfile
import traceback
from functools import wraps
from pathlib import Path
from pprint import pprint
from typing import Dict, Tuple

from vimtool import vim_helper
from vimtool.core import do_vimtool, create_todo_, load_todos_
from vimtool.handle_buffer import handle_it, delete_todo_
from vimtool.vim_helper import feedkeys

""" Python VIM Interface Wrapper """

_log = logging.getLogger("vimtool-plugin.vimtool_manager")
ROOT_DIR = Path(__file__).parent.absolute()

try:
    # import vim  # relevant for debugging, but gives error when run with main
    # noinspection PyUnresolvedReferences
    import vim
except:
    _log.debug("No vim module available outside vim")
    pass


def split_path(args: str) -> Tuple[str, str]:
    if "#" not in args:
        return args, ""
    path, *suffix = args.split("#", 1)
    suffix = "".join(suffix)
    if Path(path).suffix == ".md":
        suffix = f"#{suffix}"  # add the leading heading marker back again
    return path, suffix


def err_to_scratch_buffer(func):
    """Decorator that will catch any Exception that 'func' throws and displays
    it in a new Vim scratch buffer."""

    # Gotcha: static function, so now 'self'
    @wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)
        except Exception as e:  # pylint: disable=bare-except
            msg = """An error occured.

Following is the full stack trace:
"""
            msg += traceback.format_exc()
            vim_helper.new_scratch_buffer(msg)

    return wrapper


class VimToolManager:
    @classmethod  # classmethod always gets class as parameter
    def get_clsname(cls):
        return cls.__name__

    def __repr__(self):
        return "{self.__class__.__name__}"  # subclassing!

    def __init__(self):
        super().__init__()
        self.handler: Dict[str, str] = {
            "md": "handle_md",
        }

    @staticmethod
    def _get_locals() -> Dict[str, any]:
        locals = {
            "window": vim.current.window,
            "buffer": vim.current.buffer,
            "line": vim.current.window.cursor[0] - 1,
            "column": vim.current.window.cursor[1] - 1,
            "cursor": vim.current.window.cursor,
        }
        if _log.getEffectiveLevel() == logging.DEBUG:
            # print(vim.vars.keys())
            # print(vim.VIM_SPECIAL_PATH)
            # print(vim._get_paths())
            pprint(locals)
        return locals

    @staticmethod
    def call_vimtool(args: str):
        _log.debug(f"{args=}")
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."

        out = do_vimtool(args)
        # out = vimtool.convert(vim.current.line)

    @staticmethod
    def edit_vimtool(args: str):
        """Edits text files and jumps to first position of pattern
        pattern is extracted via separator: '#'
        """
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."

        path, suffix = split_path(args)
        _log.debug(f"{args=}, {path=}, {suffix=}")
        vim.command(f"tabnew {path}")
        if suffix != "":
            vim.command(f"/{suffix}")

    @staticmethod
    def create_todo(args: str, path: str):
        _log.debug(f"{args=}, {path=}")
        locals = VimToolManager._get_locals()
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."
        assert isinstance(path, str), f"Error: input must be string, got {type(path)}."
        id_ = create_todo_(args, path)
        vim.command(f"echom 'created/updated: {args} {id_=}'")

    @staticmethod
    @err_to_scratch_buffer
    def load_todos():
        lineno = 10
        # vim_helper.buf[lineno] = vim_helper.buf[lineno].rstrip()
        current = vim.current

        todos = load_todos_()

        temp_path = f"{tempfile.gettempdir()}/todo_tmp.md"
        _log.debug(f"{temp_path=}")

        # scratch buffer
        vim.command(f"edit {temp_path}")
        # vim.command("set buftype=nofile")

        vim.current.buffer[:] = todos

        feedkeys(r"\<Esc>")
        feedkeys(r"\<c-w>\<down>")
        vim.command("set ft=markdown")
        _log.info("Done")

    @staticmethod
    def debug():
        current = vim.current

        locals = VimToolManager._get_locals()
        # add line at end of buffer
        current.buffer[-1:0] = ["New line at end."]

    @staticmethod
    @err_to_scratch_buffer
    def handle_todos(args: str):
        # path = vim.eval("@%")  # relative path
        path = vim.eval("expand('%:p')")
        _log.debug(f"{args=}, {path=}")
        if args == "read":  # autocmd bufread
            new_text = handle_it(vim.current.buffer[:], path, read=True)
        else:  # autocmd bufwrite
            new_text = handle_it(vim.current.buffer[:], path, read=False)
        vim.current.buffer[:] = new_text

    @staticmethod
    @err_to_scratch_buffer
    def delete_todo(args: str, path: str):
        _log.debug(f"{args=}, {path=}")
        locals = VimToolManager._get_locals()
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."
        assert isinstance(path, str), f"Error: input must be string, got {type(path)}."
        # id_ = create_todo_(args, path)
        id_ = delete_todo_(args, path)
        vim.command(f"echom 'deleted: {args} {id_=}'")

    @staticmethod
    @err_to_scratch_buffer
    def throw_error(args: str, path: str):
        _log.debug(f"{args=}, {path=}")
        raise Exception(f"Exception Test")
