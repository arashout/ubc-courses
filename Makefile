help:
	@echo "Usage:"
	@echo "    make help        show this message"
	@echo "    make setup       create virtual environment and install dependencies"
	@echo "    make activate    enter virtual environment"
	@echo "    make test        run the test suite"
	@echo "    exit             leave virtual environment"

setup:
	pip3 install pipenv
	# Use python3 for the enviroment
	pipenv install --dev --python=3.6

activate:
	pipenv shell -c

test:
	pipenv run python3 test_models.py

.PHONY: help activate test