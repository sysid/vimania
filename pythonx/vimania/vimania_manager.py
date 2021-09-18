import logging
import tempfile
import traceback
from functools import wraps
from pathlib import Path
from pprint import pprint
from typing import Dict, Tuple

from vimania import vim_helper
from vimania.core import do_vimania, create_todo_, load_todos_, delete_twbm
from vimania.exception import VimaniaException
from vimania.handle_buffer import handle_it, delete_todo_
from vimania.vim_helper import feedkeys

""" Python VIM Interface Wrapper """

_log = logging.getLogger("vimania-plugin.vimania_manager")
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
        # noinspection PyBroadException
        try:
            return func(*args, **kwds)
        except Exception as e:  # pylint: disable=bare-except
            msg = """An error occured.

Following is the full stack trace:
"""
            msg += traceback.format_exc()
            vim_helper.new_scratch_buffer(msg)

    return wrapper


def warn_to_scratch_buffer(func):
    """Decorator that will catch any Exception that 'func' throws and displays
    it in a new Vim scratch buffer."""

    # Gotcha: static function, so now 'self'
    @wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)
        except VimaniaException as e:  # pylint: disable=bare-except
            msg = str(e)
            vim_helper.new_scratch_buffer(msg)

    return wrapper


class VimaniaManager:
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
    @err_to_scratch_buffer
    @warn_to_scratch_buffer
    def call_vimania(args: str, save_twbm: str):
        _log.debug(f"{args=}, {save_twbm=}")
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."

        # https://vim.fandom.com/wiki/User_input_from_a_script
        return_message = do_vimania(args, False if int(save_twbm) == 0 else True)
        if return_message != "":
            vim.command(f"echom '{return_message}'")

    @staticmethod
    @err_to_scratch_buffer
    def edit_vimania(args: str):
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
    @err_to_scratch_buffer
    def create_todo(args: str, path: str):
        _log.debug(f"{args=}, {path=}")
        locals = VimaniaManager._get_locals()
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
    @err_to_scratch_buffer
    def debug():
        current = vim.current

        locals = VimaniaManager._get_locals()
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
        locals = VimaniaManager._get_locals()
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."
        # id_ = create_todo_(args, path)
        id_ = delete_todo_(args, path)
        vim.command(f"echom 'deleted: {args} {id_=}'")

    @staticmethod
    # https://github.com/vim/vim/issues/6017: cannot create error buffer
    # @err_to_scratch_buffer
    # @warn_to_scratch_buffer
    def delete_twbm(args: str):
        _log.debug(f"{args=}")
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."
        try:
            id_, url = delete_twbm(args)
        except VimaniaException as e:
            vim.command(
                f"echohl WarningMsg | echom 'Cannot extract url from: {args}' | echohl None"
            )
            return
        vim.command(f"echom 'deleted twbm: {url} {id_=}'")

    @staticmethod
    @err_to_scratch_buffer
    def throw_error(args: str, path: str):
        _log.debug(f"{args=}, {path=}")
        raise Exception(f"Exception Test")
