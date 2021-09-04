#!/usr/bin/env bash
#vim '+Vader!*' && echo Success || echo Failure' && echo Success || echo Failure

source ~/dev/binx/profile/sane_bash.sh

cp -v data/todos.db.empty data/vader.db

if [ -z "$1" ]; then
    echo "-E- no testfiles given."
    echo "runall: $0 '*'"
    exit 1
fi

TW_VIMTOOL_DB_URL=sqlite:///data/vader.db vim -Nu <(cat << EOF
filetype off
set rtp+=~/.vim/plugged/vader.vim
set rtp+=~/.vim/plugged/vim-misc
set rtp+=~/.vim/plugged/scriptease
set rtp+=~/.vim/plugged/vim-textobj-user
set rtp+=~/dev/vim/tw-vim
set rtp+=~/dev/vim/vimtool
filetype plugin indent on
syntax enable

let g:twvim_debug = 1
let g:os = 'Darwin'
if g:twvim_debug | echom "-D- Debugging is activated." | endif

" required by tw-vim
let g:twvim_config = {
      \ 'diary_path': '/Users/Q187392/vimwiki/diary',
\ }

" to aovid prompting
set shortmess+=at
"set cmdheight=200
packadd cfilter
EOF) "+Vader! $1" && Green Success || Red Failure

