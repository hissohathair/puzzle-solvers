# Makefile

RUNTEST=PYTHONPATH=$PYTHONPATH:.. python -m unittest -v -b
COVERAGE=coverage

ALLTESTS=$(patsubst %.py, %.py, $(wildcard tests/test_*.py))

default: test

test:
		${RUNTEST} ${ALLTESTS}

coverage:
		SUDOKU_LONG_TESTS=1 ${COVERAGE} run -m unittest discover
		${COVERAGE} report -m
		${COVERAGE} html --directory=tests/htmlcov

all: test coverage

% : test_%.py
		${RUNTEST} test_$@

clean:
	rm -rf __pycache__ puzzle/__pycache__ tests/__pycache__ .coverage
