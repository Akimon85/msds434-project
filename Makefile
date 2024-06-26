python3: -m venv ~/.msds434-project

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

#test:
#	python -m pytest -vv test_hello.py

test:
	python -m pytest -vv main.py

format:
	black *.py

lint:
	pylint --disable=R,C hello.py

all: install lint test
