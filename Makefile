.PHONY: sync sync-mcp sync-skills check-sync help

help:
	@echo "Kaggle Skills - Available targets:"
	@echo "  make sync       Sync skills + instructions (safe for existing projects)"
	@echo "  make sync-mcp   Sync skills + MCP configs (overwrites existing MCP)"
	@echo "  make sync-skills  Sync skills only, skip instruction files"
	@echo "  make check-sync   Check if generated files are up to date"

sync:
	python tools/sync_agent_assets.py

sync-mcp:
	python tools/sync_agent_assets.py --mcp

sync-skills:
	python tools/sync_agent_assets.py --skills-only

check-sync:
	python tools/sync_agent_assets.py --check
