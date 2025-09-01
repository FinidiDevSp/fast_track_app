PY=python

venv:
	$(PY) -m venv .venv

install:
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --port 8000

test:
	. .venv/bin/activate && pytest --cov=app --cov-report=term-missing

fmt:
	. .venv/bin/activate && black app tests

lint:
	. .venv/bin/activate && ruff check app tests
