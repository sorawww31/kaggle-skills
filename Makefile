.PHONY: sync check-sync help

help:
	@echo "Kaggle Skills - Available targets:"
	@echo "  make sync         Sync agent assets to all editor adapters"
	@echo "  make check-sync   Check if generated files are up to date"

sync:
	python tools/sync_agent_assets.py

check-sync:
	python tools/sync_agent_assets.py --check
