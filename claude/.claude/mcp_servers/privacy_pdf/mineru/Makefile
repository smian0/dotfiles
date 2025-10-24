.PHONY: help convert batch clean install update-deps test

help: ## Show this help message
	@echo 'Usage:'
	@echo '  make <target>'
	@echo ''
	@echo 'Targets:'
	@awk -F ':|##' '/^[^\t].+?:.*?##/ { printf "  %-20s %s\n", $$1, $$NF }' $(MAKEFILE_LIST)

install: ## Install MinerU and its dependencies (creates venv)
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Installing MinerU core package..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install uv
	./venv/bin/uv pip install -U "mineru[core]"
	@echo "✅ MinerU installed successfully!"
	@echo "Run 'make test' to verify installation"

convert: ## Convert PDF to markdown (Usage: make convert FILE=path/to/file.pdf [OUTPUT=output_dir])
	@if [ -z "$(FILE)" ]; then \
		echo "Error: FILE parameter is required."; \
		echo "Usage: make convert FILE=path/to/file.pdf [OUTPUT=output_dir]"; \
		exit 1; \
	fi
	@if [ -z "$(OUTPUT)" ]; then \
		OUTPUT_DIR=$$(dirname "$(FILE)")/mineru_output; \
	else \
		OUTPUT_DIR="$(OUTPUT)"; \
	fi; \
	echo "Converting $(FILE) to $$OUTPUT_DIR..."; \
	./venv/bin/mineru -p "$(FILE)" -o "$$OUTPUT_DIR"

batch: ## Batch convert all PDFs in directory (Usage: make batch DIR=path/to/pdfs [OUTPUT=output_dir])
	@if [ -z "$(DIR)" ]; then \
		echo "Error: DIR parameter is required."; \
		echo "Usage: make batch DIR=path/to/pdfs [OUTPUT=output_dir]"; \
		exit 1; \
	fi
	@if [ -z "$(OUTPUT)" ]; then \
		OUTPUT_DIR="$(DIR)/mineru_output"; \
	else \
		OUTPUT_DIR="$(OUTPUT)"; \
	fi; \
	echo "Batch converting PDFs from $(DIR) to $$OUTPUT_DIR..."; \
	for pdf in "$(DIR)"/*.pdf; do \
		if [ -f "$$pdf" ]; then \
			echo "Processing: $$pdf"; \
			./venv/bin/mineru -p "$$pdf" -o "$$OUTPUT_DIR"; \
		fi; \
	done

test: ## Test MinerU installation
	@echo "Testing MinerU installation..."
	@./venv/bin/mineru -h > /dev/null 2>&1 && \
		echo "✅ MinerU is installed and working!" || \
		echo "❌ MinerU test failed. Run 'make install' to reinstall."

update-deps: ## Update MinerU to latest version
	@echo "Updating MinerU..."
	./venv/bin/uv pip install -U "mineru[core]"
	@echo "✅ MinerU updated successfully!"

clean: ## Clean up temporary and generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleaned up temporary files"

clean-all: ## Remove virtual environment and all generated files
	@echo "⚠️  This will remove the virtual environment. Continue? [y/N] " && read ans && [ $${ans:-N} = y ]
	rm -rf venv
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Removed virtual environment and cleaned all files"
	@echo "Run 'make install' to reinstall"

fix-opengl: ## Fix OpenGL library path issues on Apple Silicon
	@echo "Applying OpenGL fix for Apple Silicon..."
	@echo "Unsetting DYLD_LIBRARY_PATH..."
	@unset DYLD_LIBRARY_PATH || true
	@echo "✅ OpenGL fix applied"
	@echo "If issues persist, add this to ~/.zshrc:"
	@echo "export DYLD_LIBRARY_PATH=/System/Library/Frameworks/OpenGL.framework/Versions/A/Libraries"
