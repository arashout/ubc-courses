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
	pipenv install --dev --python=3.6

	# Install NPM packages
	npm install -g typescript
	npm install -g serverless
	npm install

	# Install 
	sls plugin install -n serverless-wsgi
	sls plugin install -n serverless-python-requirements
 build_client:
	./scripts/build.sh
 local_deploy:
	sls wsgi serve
 deploy:
	./scripts/build.sh
	sls deploy
 activate:	
	pipenv shell
 test:	
	pipenv run python3 test_models.py	

 .PHONY: help activate test 