.PHONY: help install install-dev test lint format build docker-build helm-install clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package
	pip install -e .

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pip install -e .

test: ## Run tests
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v -m integration

lint: ## Run linting
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/

build: ## Build the package
	python -m build

docker-build: ## Build Docker image
	docker build -t gwaines/security-operator:latest .

docker-push: ## Push Docker image
	docker push gwaines/security-operator:latest

helm-install: ## Install Helm chart
	helm install security-operator helm-chart/

helm-upgrade: ## Upgrade Helm chart
	helm upgrade security-operator helm-chart/

helm-package: ## Package Helm chart
	mkdir -p dist
	helm package helm-chart/ -d dist/

apply-crds: ## Apply CRDs to Kubernetes
	kubectl apply -f crds/

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete