# core.py
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

from vimtool.db.dal import DAL, TodoStatus, Todo
from vimtool.environment import config
from vimtool.handle_buffer import VimTodo
from vimtool.rifle.rifle import Rifle

""" Implementation independent of vim """

_log = logging.getLogger("vimtool-plugin.core")
ROOT_DIR = Path(__file__).parent.absolute()

if sys.platform.startswith("win32"):
    OS_OPEN = "explorer.exe"
elif sys.platform.startswith("linux"):
    OS_OPEN = "xdg-open"
# Linux-specific code here...
elif sys.platform.startswith("darwin"):
    OS_OPEN = "open"
else:
    OS_OPEN = None


def get_mime_type(uri: str) -> str:
    # mimetypes.init()
    # return mimetypes.guess_type(p)

    # rifle has more hits
    rifle = Rifle(
        f"{ROOT_DIR}/rifle/rifle.conf"
    )  # GOTCHA: must be initialized for every call, otherwise same result
    rifle.reload_config()
    return rifle.get_mimetype(uri)


def is_text(uri: str) -> bool:
    return get_mime_type(uri).startswith("text")


def do_vimtool(args: str):
    if OS_OPEN is None:
        _log.error(f"Unknown OS architecture: {sys.platform}")
        return

    if not isinstance(args, str):
        _log.error(f"wrong args type: {type(args)}")
        return 1

    _log.info(f"{args=}")
    p = Path.home()  # default setting

    if args.startswith("http"):
        _log.debug(f"Http Link")
        p = args
    elif args[0] in "/,.,~,$":
        if args.startswith("/"):
            _log.debug(f"Absolute path.")
            p = Path(args)
        elif args.startswith("~"):
            _log.debug(f"Path with prefix tilde.")
            p = Path(args).expanduser().absolute()
        elif args.startswith("$"):
            _log.debug(f"Path with environment prefix.")
            p = Path(args)
            env_path = os.getenv(p.parts[0].strip("$"), None)
            if env_path is None:
                _log.warning(f"{p.parts[0]} not set in environment. Cannot proceed.")
                return
            p = Path(env_path) / Path(*p.parts[1:])
        elif args.startswith("."):
            _log.debug(f"Relative path: {args}, working dir: {os.getcwd()}")
            p = Path(args).absolute()

        if not p.exists():
            _log.warning(f"{p} does not exists.")
            return
    else:
        _log.warning(f"Unknown protocol: {args=}")
        return

    _log.info(f"Opening: {p}")
    subprocess.run([OS_OPEN, p])


def create_todo_(args: str, path: str) -> int:
    todo = parse_todo_str(args)
    todo.path = path

    with DAL(env_config=config) as dal:
        todos = dal.get_todos(fts_query=todo.todo)
        if len(todos) >= 1:
            active_todos = [todo for todo in todos if todo.flags < TodoStatus.DONE]
            if len(active_todos) > 1:
                raise ValueError(
                    f"Same active todo already exists: {[td.id for td in active_todos]}. Clear DB inconsistency"
                )
            elif len(active_todos) == 1 and active_todos[0].id is not None:
                _log.debug(f"Updating todo: {todo.todo}")
                id_ = dal.update_todo(todo)
            else:
                _log.debug(f"Creating todo: {todo.todo}")
                id_ = dal.insert_todo(todo)


def parse_todo_str(args: str) -> Todo:
    pattern = re.compile(r"""(- \[.+])(.*)""", re.MULTILINE)
    todo_status, todo = pattern.findall(args)[0]
    if todo_status == "- [ ]":
        flag = 0
    elif todo_status == "- [-]":
        flag = 1
    elif todo_status == "- [x]" or todo_status == "- [X]":
        flag = 2
    else:
        flag = 99  # unknown status
    todo = Todo(
        todo=todo.strip(),
        flags=flag,
        created_at=datetime.utcnow(),
    )
    return todo


def load_todos_() -> Sequence[str]:
    with DAL(env_config=config) as dal:
        todos = dal.get_todos(fts_query="")
        vtds = list()

        for todo in todos:
            vtd = VimTodo(
                raw_code=f"%%{todo.id}%%",
                todo=todo.todo,
            )
            vtd.set_status(todo.flags)
            vtds.append(vtd)
    return [vtd.vim_line for vtd in vtds]


if __name__ == "__main__":
    arg = "$HOME/dev/vim/vim-textobj-uri/test/vimtool//vimtool.pdf"
    do_vimtool("my-args-given")
