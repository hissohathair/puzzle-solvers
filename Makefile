# Makefile

RUNTEST=python -m unittest -v -b
COVERAGE=coverage

ALLMODULES=$(patsubst %.py, %.py, $(wildcard test_*.py))

all: test coverage

test:
		${RUNTEST} ${ALLMODULES}

coverage:
		${COVERAGE} run -m unittest discover
		${COVERAGE} report -m
		${COVERAGE} html

% : test_%.py
		${RUNTEST} test_$@
