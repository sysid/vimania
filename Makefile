# You can set these variables from the command line, and also from the environment for the first two.
SOURCEDIR     = source
BUILDDIR      = build
TESTDIR       = tests
MAKE          = make
PACKAGE		  = 'vimania'

VERSION       = $(shell cat pythonx/vimania/__init__.py | grep __version__ | sed "s/__version__ = //" | sed "s/'//g")

.DEFAULT_GOAL := help

isort = isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 $(pkg_src) $(tests_src)
black = black $(pkg_src) $(tests_src)
tox = tox
mypy = mypy $(pkg_src)
pipenv = pipenv

.PHONY: all
all: clean build upload tag
	@echo "--------------------------------------------------------------------------------"
	@echo "-M- building and distributing"
	@echo "--------------------------------------------------------------------------------"

.PHONY: test
test:  ## run tests
	TW_VIMANIA_DB_URL=sqlite:///tests/data/vimania_todos_test.db python -m py.test tests -vv

.PHONY: test-vim
test-vim:  ## run tests-vim
	pushd tests; ./run_test.sh test_textobj_uri.vader; ./run_test.sh test_vimania_vim.vader; popd

#.PHONY: coverage
#coverage:  ## Run tests with coverage
#	python -m coverage erase
#	#python -m coverage run --include=$(pkg_src)/* --omit="$(pkg_src)/text.py" -m pytest -ra
#	TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db python -m coverage run --include=$(pkg_src)/* -m pytest -ra
#	#python -m coverage report -m
#	python -m coverage html
#	python -m coverage report -m
#	python -m coverage xml
#	open htmlcov/index.html  # work on macOS

.PHONY: clean
clean:  ## remove ./dist
	@echo "Cleaning up..."
	#git clean -Xdf
	rm -rf ./pythonx/dist
	rm -rf ./pythonx/*.egg-info

.PHONY: build
build: clean-vim ## build
	@echo "building"
	#python setup.py sdist
	pushd pythonx; python -m build; popd

.PHONY: upload
upload:  ## upload to PyPi
	@echo "upload"
	twine upload --verbose pythonx/dist/*

.PHONY: clean-vim
clean-vim:  ## clean pythonx directory
	@echo "Removing python packages from pythonx"
	@pushd pythonx; git clean -d -x -f; popd

.PHONY: build-vim
build-vim:  ## copy all python packages into pythonx
	./scripts/cp_venv.sh dev

.PHONY: tag
tag:  ## tag with VERSION
	@echo "tagging $(VERSION)"
	git tag -a $(VERSION) -m "version $(VERSION)"
	git push --tags

.PHONY: black
black: clean-vim  ## format with black
	@echo "Formatting with black"
	#black --check --verbose --exclude="twbm/buku.py" .
	black pythonx/vimania

.PHONY: install
install: clean-vim uninstall  ## pipx install
	pipx install $(HOME)/dev/vim/vimania/pythonx

.PHONY: uninstall
uninstall:  ## pipx uninstall
	-pipx uninstall vimania

.PHONY: bump-minor
bump-minor:  ## bump-minor
	bumpversion --verbose minor

.PHONY: bump-patch
bump-patch:  ## bump-patch
	#bumpversion --dry-run --allow-dirty --verbose patch
	bumpversion --verbose patch

.PHONY: copy-buku
copy-buku:  ## copy-buku: copy buku.py from twbm
	cp $(HOME)/dev/py/twbm/twbm/buku.py $(HOME)/dev/vim/vimania/pythonx/vimania/buku.py

.PHONY: develop
develop: _confirm clean-vim ## develop python module, prep accordingly
	pycharm .

.PHONY: _confirm
_confirm:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo "Action confirmed by user."

.PHONY: help
help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
