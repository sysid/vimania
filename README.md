# vimtool
Based on:

1. Install [vim-textobj-user](https://github.com/kana/vim-textobj-user)
2. Install [vim-textobj-uri](https://github.com/jceb/vim-textobj-uri)

   cd ~/.vim/bundle
   git clone https://github.com/jceb/vim-textobj-uri.git

## Patterns from vim-textobj-uri
- positioning patterns cover markdown: `[name](uri)`

## Patterns added:
`file://`: allow all characters in uri, resolves relative paths with environment variables
`vim::`: call `VimtoolEdit`

## Operations
### Reset database
Rrequires to clean existing markdown files with todos:   
1. Reset DB: `cd pythonx/vimtool/db; rm todos.db; alembic upgrade head`
2. Clean up existing markdown files:
   - find all affected markdown files: `rg -t md -- '-%\d+%'`
   - edit the markdown files and remove the allocated database-id to allow for re-init: `sed -i 's/-%[0-9]\+%/-/' todo.md`

## Development
### Preparation
- clear the `pythonx` directory from bundled libs: `make clean-vim`

### Testing
Preparation: Make sure that the working directory of test-runs is the project-root (e.g. in PyCharm)  

For python development it is important to restart vim after every change in order to enforce proper reload: 
use Vader script: `run_tests.sh testfile` in tests directory.

run python tests: `make test`
run integration tests with vim and pyhthon: `make test-vim`

#### textobj
- Use vim mapping `go` on the `*.vader` URIs.


### Deployment

# Example
Example for registration of additional object and their handler:
```vim
" location: after/plugin/textobj_uri.vim
if ! exists('g:loaded_uri')
  echom "-W- vim-textobj-uri not availabe, please install."
  finish
endif

if g:twvim_debug | echom "-D- vim-textobj-uri is installed, registering patterns." | endif
" example pattern
URIPatternAdd! vimtool://\%(\([^()]\+\)\) :silent\ !open\ "%s"
```


# TODO
todo status enum: [enum](https://stackoverflow.com/questions/5299267/how-to-create-enum-type-in-sqlite)
todos link check from DB

- [-] documentation
- [x] exclude code fences (todos would be evaluated)
- [-] hierarchical todos
- [ ] vimtool:: protocol needs clarification vs. file://

## Workflow:
1. use Ultisnip to insert 'todo' effectively in the rigth format
2. saving creates todo in DB and adds reference to DB to markdown

## Development

### Test Harness
Regex: https://regex101.com/r/LpSX0i/1

### Manual todo testing
reset db: `alembic upgrade head`
TW_VIMTOOL_DB_URL="sqlite:///$PROJ_DIR/pythonx/vimtool/db/todos.db" vim tests/todo.md# vimtool
# vimania
