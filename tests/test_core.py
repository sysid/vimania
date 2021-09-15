import re

import pytest

from vimania.core import do_vimania, get_mime_type, create_todo_, parse_todo_str, delete_twbm


# @pytest.mark.skip("Interactive test.")
@pytest.mark.parametrize(
    ("uri",),
    (
            # ("/Users/Q187392/dev/vim/vimania/tests/data/vimania.pdf",),
            # ("$HOME/dev/vim/vimania/tests/data/vimania.pdf",),
            # ("/Users/Q187392/dev/vim/vimania/tests/data///vimania.pdf",),
            # ("https://www.google.com",),
            # ("./tests/data/tsl-handshake.png",),
            ("./tests/data/test.md",),
    ),
)
def test_do_vimania(uri):
    # arg = "$HOME/dev/vim/vim-textobj-uri/test/vimania//vimania.pdf"
    do_vimania(uri)


@pytest.mark.parametrize(
    ("uri", "result"),
    (
            ("/Users/Q187392/dev/vim/vimania/tests/data/vimania.pdf", "application/pdf"),
            ("/Users/Q187392/dev/vim/vimania/tests/data/x.html", "text/html"),
            ("/Users/Q187392/dev/vim/vimania/tests/data/tsl-handshake.png", "image/png"),
            ("/Users/Q187392/dev/vim/vimania/tests/data/test.md", "text/plain"),
            ("https://www.google.com", "application/x-msdownload"),
            ("mailto:xxx@bla.com", "application/x-msdownload"),
    ),
)
def test_get_mimetype(uri, result):
    # arg = "$HOME/dev/vim/vim-textobj-uri/test/vimania//vimania.pdf"
    print(get_mime_type(uri))
    assert get_mime_type(uri) == result


@pytest.mark.parametrize(
    ("uri", "todo_status", "todo"),
    (
            ("- [ ] bla blub", 0, "bla blub"),
            ("- [-] bla blub", 1, "bla blub"),
            ("- [x] bla blub", 2, "bla blub"),
            ("- [X] bla blub", 2, "bla blub"),
    ),
)
def test_parse_todo_str(uri, todo_status, todo):
    under_test = parse_todo_str(uri)
    assert under_test.flags == todo_status
    assert under_test.todo == todo
    _ = None


@pytest.mark.parametrize(
    ("uri", "path", "result"),
    (("- [ ] todo 5", "testpath", "two active todos already exist, DB inconsistenty"),),
)
def test_create_invalid_todo_db_inconsistency(uri, path, result):
    with pytest.raises(ValueError):
        create_todo_(uri, path)


@pytest.mark.parametrize(
    ("uri", "path", "result"),
    (("- [ ] todo yyy", "testpath", "new todo"),),
)
def test_create_todo(uri, path, result):
    create_todo_(uri, path)  # TODO assert missing


# @pytest.mark.parametrize(
#     ("uri", "path", "result"),
#     (("- [ ] todo 6", "testpath", "update existing todo"),),
# )
# def test_update_todo(uri, path, result):
#     create_todo_(uri, path)  # TODO assert missing

@pytest.mark.parametrize(
    ("line", "result"),
    (
            ("[testuri](vm::http://www.test.org)", "http://www.test.org"),
            ("asdf http://www.google.com asdf", "http://www.google.com"),
            ("balaser https://my.net asdf", "https://my.net"),
            ("[testuri](vm::http://www.test.org) adf", "http://www.test.org"),
            ("[testuri](vm::http://www.test.org#adf?asdf&xxxx aaaaaaa", "http://www.test.org#adf?asdf&xxxx"),
            ("[testuri](vm::http://www.test.org)adf", "http://www.test.org"),
    )
)
def test_delete_twbm_regexp(mocker, line, result):
    # https://regex101.com/r/W9Epg0/1
    # https://regex101.com/delete/gn3L5TNGXye9ajzZf5szoY5G
    # spy = mocker.patch("vimania.core.BukuDb")
    # delete_twbm(line)
    assert re.compile(
        r""".*(https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b[-a-zA-Z0-9@:%_\+.~#?&\/=]*)"""
    ).match(line).group(1) == result
