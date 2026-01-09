# ==============================================================================
# SentinelFlow Project Makefile (Windows Fixed)
# ==============================================================================

# Configuration Variables
RG_NAME = SentinelFlow-RG
LOCATION = swedencentral
PYTHON_V = 3.11
VENV_DIR = .venv
BACKEND_DIR = backend
INFRA_DIR = infra
TEST_DIR = tests

# Azure Bicep File
BICEP_FILE = $(INFRA_DIR)/main.bicep

# ==============================================================================
# 1. Local Development & Setup
# ==============================================================================

.PHONY: setup
setup:
	@echo "Creating Python virtual environment..."
	python -m venv $(VENV_DIR)
	@echo "Installing dependencies..."
	$(VENV_DIR)/Scripts/pip install -r $(BACKEND_DIR)/requirements.txt
	$(VENV_DIR)/Scripts/pip install pytest
	@echo "Setup complete."

.PHONY: test
test:
	@echo "Running Unit Tests..."
	pytest $(TEST_DIR)/

.PHONY: run-local
run-local:
	@echo "Starting Azure Functions locally..."
	cd $(BACKEND_DIR) && func start

# ==============================================================================
# 2. Cloud Infrastructure (Infrastructure as Code)
# ==============================================================================

.PHONY: infra-create
infra-create:
	@echo "Creating Resource Group: $(RG_NAME)..."
	az group create --name $(RG_NAME) --location $(LOCATION)
	@echo "Deploying Bicep Template..."
	az deployment group create --resource-group $(RG_NAME) --template-file $(BICEP_FILE) --name main

.PHONY: infra-update
infra-update:
	@echo "Updating Infrastructure configuration..."
	az deployment group create --resource-group $(RG_NAME) --template-file $(BICEP_FILE) --name main

# ==============================================================================
# 3. Application Deployment (FIXED FOR WINDOWS)
# ==============================================================================

.PHONY: deploy-code
deploy-code:
	@echo "Deploying to Azure Function App using Python wrapper..."
	@python -c "import subprocess, os; app_name = subprocess.check_output('az deployment group show --resource-group $(RG_NAME) --name main --query properties.outputs.functionAppName.value -o tsv', shell=True).decode().strip(); print(f'Target App: {app_name}'); os.chdir('$(BACKEND_DIR)'); os.system(f'func azure functionapp publish {app_name} --build remote')"

.PHONY: deploy-all
deploy-all: infra-create deploy-code
	@echo "Full deployment complete."

# ==============================================================================
# 4. Utilities & Teardown
# ==============================================================================

.PHONY: get-url
get-url:
	@echo "Fetching Function App URL..."
	@az deployment group show --resource-group $(RG_NAME) --name main --query "properties.outputs.functionAppName.value" -o tsv

.PHONY: clean
clean:
	@echo "Cleaning up local cache files using Python..."
	@python -c "import shutil, os; dirs = ['$(BACKEND_DIR)/__pycache__', '$(TEST_DIR)/__pycache__', '$(BACKEND_DIR)/.python_packages']; [shutil.rmtree(d, ignore_errors=True) for d in dirs]"

.PHONY: destroy
destroy:
	@echo "WARNING: This will permanently delete Resource Group: $(RG_NAME)"
	@echo "Waiting 5 seconds... Press Ctrl+C to cancel."
	@python -c "import time; time.sleep(5)"
	az group delete --name $(RG_NAME) --yes --no-wait
	@echo "Deletion initiated. Resources will be removed in the background."