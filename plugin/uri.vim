" uri.vim:      Textobjects for dealing with URIs
" Author:       sysid, based on work from Jan Christoph Ebersbach <jceb@e-jc.de>
" Dependecy:    twbm, vim-textobj-user
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

" opens the URI no saving action triggered
nnoremap <Plug>TextobjURIOpen :<C-u>call <sid>TextobjURIOpen(0)<CR>
command! TextobjURIOpen :call <sid>TextobjURIOpen(0)

" opens the URI and saves it to URI DB from twbm module (python)
nnoremap <Plug>TextobjURIOpenSave :<C-u>call <sid>TextobjURIOpen(1)<CR>
command! TextobjURIOpenSave :call <sid>TextobjURIOpen(1)

if ! hasmapto('<Plug>TextobjURIOpen', 'n')
    nmap go <Plug>TextobjURIOpen
endif

if ! hasmapto('<Plug>TextobjURIOpenSave', 'n')
    nmap goo <Plug>TextobjURIOpenSave
endif

let g:loaded_uri = 1
