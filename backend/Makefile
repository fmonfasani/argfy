.PHONY: venv install dev test lint docker-build docker-run

PY      := python
VENV    := .venv
ACT     := source $(VENV)/Scripts/activate
PIP     := $(VENV)/Scripts/pip

venv:                         ## Crea entorno virtual
	$(PY) -m venv $(VENV)

install: venv                ## Instala dependencias
	$(ACT) && $(PIP) install -r requirements.txt

dev:                          ## Arranca FastAPI con recarga
	$(ACT) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:                         ## Ejecuta pytest
	$(ACT) && pytest -q

lint:                         ## Ruff + mypy
	$(ACT) && ruff check app && mypy app

docker-build:                 ## Imagen para producción
	docker build -t argfy-backend .

docker-run:                   ## Corre contenedor local
	docker run --rm -p 8000:8000 argfy-backendmake