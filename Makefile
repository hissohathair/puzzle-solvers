# Makefile

RUNTEST=python -m unittest -v -b
COVERAGE=coverage

ALLMODULES=$(patsubst %.py, %.py, $(wildcard test_*.py))

default: test

test:
		${RUNTEST} ${ALLMODULES}

coverage:
		SUDOKU_LONG_TESTS=1 ${COVERAGE} run -m unittest discover
		${COVERAGE} report -m
		${COVERAGE} html

all: test coverage

% : test_%.py
		${RUNTEST} test_$@
