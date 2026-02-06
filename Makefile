.PHONY: install run-interface run-strategy train-rl test clean docker-build docker-run

install:
	pip3 install -r requirements.txt

run-interface:
	python3 scripts/run_interface.py

run-strategy:
	python3 scripts/run_strategy.py --strategy symmetric

train-rl:
	python3 scripts/train_rl.py --episodes 1000

test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

docker-build:
	docker build -t proptrade .

docker-run:
	docker run -p 8000:8000 proptrade

docker-compose-up:
	docker-compose up

docker-compose-down:
	docker-compose down
