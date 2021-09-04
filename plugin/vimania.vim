if exists('g:loaded_vimtool')
    finish
endif

if g:twvim_debug | echom "-D- Sourcing " expand('<sfile>:p') | endif
let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')

augroup Vimtool
 autocmd!
 autocmd BufRead *.md call VimtoolHandleTodos("read")
 autocmd BufWritePre *.md call VimtoolHandleTodos("write")
 "autocmd TextYankPost *.md echom v:event
 autocmd TextYankPost *.md
    \ if len(v:event['regcontents']) == 1 && v:event['regcontents'][0] =~? '%\d\+%' && v:event['operator'] == 'd'
    \ | call VimtoolDeleteTodo(v:event['regcontents'][0], expand('%:p'))
    \ | endif
augroup END

let g:loaded_vimtool = 1
