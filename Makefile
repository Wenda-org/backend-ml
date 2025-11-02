IMAGE_NAME := wenda-ml
TAG := latest
CONTAINER := wenda-ml-dev
PORT ?= 8000
PYTHON ?= python3.11
PIP ?= pip3
WORKDIR := /app

.PHONY: help build docker-run dev-run run install clean shell db-check migrate test

help:
	@printf "Available targets:\n"
	@printf "  venv         - Create local Python venv\n"
	@printf "  act          - Activate venv\n"
	@printf "  install      - Install dependencies\n"
	@printf "  build        - Build Docker image\n"
	@printf "  docker-run   - Run container normally\n"
	@printf "  dev-run      - Run container with volume mount (live code)\n"
	@printf "  clean        - Remove container and image\n"

venv:
	$(PYTHON) -m venv .venv

act:
	source .venv/bin/activate

install:
	@echo "Installing Python deps..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

start:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

build:
	@echo "Building docker image $(IMAGE_NAME):$(TAG)..."
	docker build -t $(IMAGE_NAME):$(TAG) .

docker-run: build
	@echo "Running docker container (normal mode)..."
	if [ -f .env ]; then ENVFILE="--env-file .env"; else ENVFILE=""; fi; \
	docker run --rm -it -p $(PORT):8000 $$ENVFILE --name $(CONTAINER) $(IMAGE_NAME):$(TAG)

# 🧠 Modo desenvolvimento com volume (sem rebuild)
dev-run: build
	@echo "Running docker container in dev mode (with volume mount)..."
	if [ -f .env ]; then ENVFILE="--env-file .env"; else ENVFILE=""; fi; \
	docker run --rm -it \
		-p $(PORT):8000 \
		$$ENVFILE \
		-v $(shell pwd):$(WORKDIR) \
		--workdir $(WORKDIR) \
		--name $(CONTAINER) \
		$(IMAGE_NAME):$(TAG) \
		bash -c "pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)"

clean:
	@echo "Cleaning containers and images..."
	-docker rm -f $(CONTAINER) >/dev/null 2>&1 || true
	-docker rmi $(IMAGE_NAME):$(TAG) >/dev/null 2>&1 || true
