if exists('g:loaded_vimania')
    finish
endif

if g:twvim_debug | echom "-D- Sourcing " expand('<sfile>:p') | endif
let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')

augroup Vimania
 autocmd!
 autocmd BufRead *.md call VimaniaHandleTodos("read")
 autocmd BufWritePre *.md call VimaniaHandleTodos("write")
 "autocmd TextYankPost *.md echom v:event
 autocmd TextYankPost *.md
    \ if len(v:event['regcontents']) == 1 && v:event['regcontents'][0] =~? '%\d\+%' && v:event['operator'] == 'd'
    \ | call VimaniaDeleteTodo(v:event['regcontents'][0], expand('%:p'))
    \ | endif
augroup END

let g:loaded_vimania = 1
