" vim: fdm=marker ts=2 sts=2 sw=2 fdl=0
" convert_string.vim
if g:twvim_debug | echom "-D- Sourcing " expand('<sfile>:p') | endif
let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')

if !has("python3")
  echo "vim has to be compiled with +python3 to run this"
  finish
endif

" only load it once
if exists('g:twtodo_loaded')
  finish
endif

py3 << EOF
# This only runns onece via resourcing
import sys
import os
import logging
import vim
from pprint import pprint

if int(vim.eval('g:twvim_debug')) == 1:
  LOG_LEVEL = logging.DEBUG
else:
  LOG_LEVEL = (logging.INFO)

_log = logging.getLogger("vimania-plugin")

if _log.handlers == []:  # avoid adding multiple handler via re-sourcing
  handler = logging.StreamHandler(sys.stdout)
  handler.setFormatter(logging.Formatter(
      '%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s',
      datefmt='%Y-%m-%d %H:%M:%S')
  )
  _log.addHandler(handler)

_log.setLevel(LOG_LEVEL)

if 'VIRTUAL_ENV' in os.environ:
  _log.debug(f"Running in VENV: {os.environ['VIRTUAL_ENV']}")
  project_base_dir = os.environ['VIRTUAL_ENV']
  activate_this = os.path.join(project_base_dir, 'bin/activate_this.py')
  exec(open(activate_this).read(), {'__file__': activate_this})

_log.debug("------------------------------ Begin Python Init -------------------------------")
plugin_root_dir = vim.eval('s:script_dir')
_log.debug(f"{plugin_root_dir=}")

# not necessary, default path import
#sys.path.insert(0, script_dir)

import vimania
from vimania import VimaniaManager
xMgr = VimaniaManager()

if LOG_LEVEL == logging.DEBUG:
  pprint(sys.path)
  print(f"{sys.version_info=}")
  print(f"{sys.prefix=}")
  print(f"{sys.executable=}")

_log.debug("------------------------------ End Python Init -------------------------------")
EOF

""""""""""""""": TODO
"redraw

function! Vimania(args)
  call TwDebug(printf("Vimania args: %s", a:args))
  python3 xMgr.call_vimania(vim.eval('a:args'))
endfunction
command! -nargs=1 Vimania call Vimania(<f-args>)
"nnoremap Q :Vimania /Users/Q187392/dev/vim/vimania/tests/data/test.md<CR>

function! VimaniaEdit(args)
  call TwDebug(printf("Vimania args: %s", a:args))
  python3 xMgr.edit_vimania(vim.eval('a:args'))
endfunction
command! -nargs=1 VimaniaEdit call VimaniaEdit(<f-args>)
"nnoremap Q :VimaniaEdit /Users/Q187392/dev/vim/vimania/tests/data/test.md<CR>
nnoremap Q :VimaniaEdit /Users/Q187392/dev/vim/vimania/tests/data/test.md#Working<CR>

function! VimaniaTodo(args, path)
  call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xMgr.create_todo(vim.eval('a:args'), vim.eval('a:path'))
endfunction
command! -nargs=1 VimaniaTodo call VimaniaTodo(<f-args>, expand('%:p'))
"noremap Q :VimaniaTodo - [ ] todo vimania<CR>

function! VimaniaLoadTodos()
  "call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xMgr.load_todos()
endfunction
command! -nargs=0 VimaniaLoadTodos call VimaniaLoadTodos()
"noremap Q :VimaniaLoadTodos<CR>

function! VimaniaDebug()
  "call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xMgr.debug()
endfunction
command! -nargs=0 VimaniaDebug call VimaniaDebug()
"noremap Q :VimaniaDebug<CR>

function! VimaniaThrowError()
  "call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xMgr.throw_error()
endfunction
command! -nargs=0 VimaniaThrowError call VimaniaThrowError()
"noremap Q :VimaniaDebug<CR>

function! VimaniaHandleTodos(args)
  "call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xMgr.handle_todos(vim.eval('a:args'))
endfunction
command! -nargs=1 VimaniaHandleTodos call VimaniaHandleTodos(<f-args)

function! VimaniaDeleteTodo(args, path)
  call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xMgr.delete_todo(vim.eval('a:args'), vim.eval('a:path'))
endfunction
command! -nargs=1 VimaniaDeleteTodo call VimaniaDeleteTodo(<f-args>, expand('%:p'))
"noremap Q :VimaniaDeleteTodo - [ ] todo vimania<CR>

let g:twtodo_loaded = 1
