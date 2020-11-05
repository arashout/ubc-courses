help:	
	@echo "Usage:"	
	@echo "    make help        show this message"	
	@echo "    make setup       create virtual environment and install dependencies"	
	@echo "    make activate    enter virtual environment"	
	@echo "    make test        run the test suite"
	@echo "    make build_client bookmarkletify the typescript code"	
	@echo "    exit             leave virtual environment"	

setup:
	pip3 install pipenv
	# Use python3 for the enviroment
	pipenv install --dev --python=3.6.9
	pipenv lock -r > requirements.txt

	# Install NPM packages
	yarn global add typescript
	yarn install

	# Install 
	yarn sls plugin install -n serverless-wsgi
	yarn sls plugin install -n serverless-python-requirements

build_client:
	./scripts/build.sh

docker:
	docker build --tag arashout/ubccourses:0.1 .
	docker push arashout/ubccourses:0.1
docker_run:
	docker run -p 5000:5000 ubccourses:0.1
local_deploy:
	pipenv run yarn sls wsgi serve
deploy:
	./scripts/build.sh
	yarn sls deploy
activate:	
	pipenv shell
test:	
	pipenv run python3 test_models.py	

.PHONY: help activate test 