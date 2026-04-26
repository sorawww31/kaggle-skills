.PHONY: sync sync-mcp check-sync help

help:
	@echo "Kaggle Skills - Available targets:"
	@echo "  make sync         Sync skills only (safe for existing projects)"
	@echo "  make sync-mcp     Sync skills + MCP configs (overwrites existing MCP)"
	@echo "  make check-sync   Check if generated files are up to date"

sync:
	python tools/sync_agent_assets.py

sync-mcp:
	python tools/sync_agent_assets.py --mcp

check-sync:
	python tools/sync_agent_assets.py --check
