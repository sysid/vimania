" uri.vim:      Textobjects for dealing with URIs
" Author:       Jan Christoph Ebersbach <jceb@e-jc.de>
" Version:      0.4
" Dependecy:    vim-textobj-user
" Copyright:    2016 Jan Christoph Ebersbach
" License:      MIT LICENSE, see LICENSE file

if exists('g:loaded_uri')
    finish
endif

command! -bang -nargs=+ URIPatternAdd :call textobj#uri#add_pattern("<bang>", <f-args>)
command! -bang -nargs=+ URIPositioningPatternAdd :call textobj#uri#add_positioning_pattern("<bang>", <f-args>)

function! s:TextobjURIOpen(save_twbm)
    let l:url = textobj#uri#open_uri(a:save_twbm)
    redraw!
    if exists('l:url') && len(l:url)
        echom 'Opening "' . l:url . '"'
    else
        echom "No URL found"
    endif
endfunction

nnoremap <Plug>TextobjURIOpen :<C-u>call <sid>TextobjURIOpen(0)<CR>
command! TextobjURIOpen :call <sid>TextobjURIOpen(0)

nnoremap <Plug>TextobjURIOpenSave :<C-u>call <sid>TextobjURIOpen(1)<CR>
command! TextobjURIOpenSave :call <sid>TextobjURIOpen(1)

if ! hasmapto('<Plug>TextobjURIOpen', 'n')
    nmap go <Plug>TextobjURIOpen
endif

if ! hasmapto('<Plug>TextobjURIOpenSave', 'n')
    nmap goo <Plug>TextobjURIOpenSave
endif

let g:loaded_uri = 1
