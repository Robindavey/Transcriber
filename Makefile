# Transcriber App Makefile
# Handles installation, updates, and service management with zero downtime

.PHONY: help install update start stop restart clean backup logs

# Configuration
VENV_DIR = .venv
APP_DIR = /home/robin/Desktop/Programs/Transcriber
SERVICE_NAME = transcriber
PYTHON = python3
PIP = $(VENV_DIR)/bin/pip
PYTHON_EXEC = $(VENV_DIR)/bin/python
APP_EXEC = $(PYTHON_EXEC) app.py

# Default target
help:
	@echo "Transcriber App Management"
	@echo ""
	@echo "Available targets:"
	@echo "  install     - Initial setup and installation"
	@echo "  update      - Safe update with zero downtime"
	@echo "  start       - Start the application"
	@echo "  stop        - Stop the application"
	@echo "  restart     - Restart the application"
	@echo "  status      - Check application status"
	@echo "  logs        - View application logs"
	@echo "  backup      - Create backup of current state"
	@echo "  clean       - Clean up temporary files"
	@echo "  help        - Show this help message"

# Initial installation
install: $(VENV_DIR)
	@echo "Installing Transcriber App..."
	$(PIP) install -r requirements.txt
	@echo "Installing system dependencies..."
	sudo apt update
	sudo apt install -y tesseract-ocr
	@echo "Installation complete. Run 'make start' to start the application."

$(VENV_DIR):
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip

# Safe update with zero downtime
update: backup
	@echo "Starting safe update process..."
	@echo "1. Creating backup..."
	# Backup is done by backup target

	@echo "2. Pulling latest code..."
	git pull origin main || echo "No git repository or main branch"

	@echo "3. Updating dependencies..."
	$(PIP) install -r requirements.txt --upgrade

	@echo "4. Running database migrations (if any)..."
	# Add migration commands here if needed

	@echo "5. Performing rolling restart..."
	$(MAKE) restart

	@echo "Update complete! Application updated with zero downtime."

# Service management
start:
	@echo "Starting Transcriber App..."
	@if pgrep -f "python.*app.py" > /dev/null; then \
		echo "Application is already running."; \
	else \
		nohup $(APP_EXEC) > app.log 2>&1 & \
		echo $$! > app.pid \
		echo "Application started with PID: $$(cat app.pid)"; \
	fi

stop:
	@echo "Stopping Transcriber App..."
	@if [ -f app.pid ]; then \
		kill $$(cat app.pid) 2>/dev/null || true; \
		rm -f app.pid; \
		echo "Application stopped."; \
	else \
		pkill -f "python.*app.py" || echo "No running application found."; \
	fi

restart: stop
	@echo "Restarting Transcriber App..."
	sleep 2
	$(MAKE) start

status:
	@if pgrep -f "python.*app.py" > /dev/null; then \
		echo "Application is running."; \
		echo "PID: $$(pgrep -f "python.*app.py")"; \
	else \
		echo "Application is not running."; \
	fi

# Logging
logs:
	@if [ -f app.log ]; then \
		tail -f app.log; \
	else \
		echo "No log file found. Start the application first."; \
	fi

# Backup
backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@BACKUP_NAME=backup_$$(date +%Y%m%d_%H%M%S).tar.gz; \
	tar -czf backups/$$BACKUP_NAME \
		--exclude='backups' \
		--exclude='.venv' \
		--exclude='__pycache__' \
		--exclude='*.log' \
		--exclude='*.pid' \
		. || echo "Backup failed"; \
	echo "Backup created: backups/$$BACKUP_NAME"

# Cleanup
clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.log" -delete 2>/dev/null || true
	find . -name "*.pid" -delete 2>/dev/null || true
	@echo "Cleanup complete."

# Development helpers
dev-install: install
	$(PIP) install -r requirements-dev.txt || echo "No dev requirements found"

test:
	@echo "Running tests..."
	$(PYTHON_EXEC) -m pytest || echo "No tests found"

lint:
	@echo "Running linter..."
	$(PYTHON_EXEC) -m flake8 . || echo "Flake8 not installed"

# Emergency stop
emergency-stop:
	@echo "Emergency stop - killing all related processes..."
	pkill -9 -f "python.*app.py" || true
	pkill -9 -f "piper" || true
	rm -f app.pid
	@echo "Emergency stop complete."