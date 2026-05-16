PREFIX ?= $(HOME)
BINDIR ?= $(PREFIX)/bin
PI_AGENT_DIR ?= $(HOME)/.pi/agent
EXTENSION_DIR ?= $(PI_AGENT_DIR)/extensions
INSTALL ?= install

EXTENSION_NAME ?= shell-command.ts
CLI_NAME ?= howcli

.PHONY: install uninstall check

install:
	uv tool install --force --refresh --reinstall ./howcli-cache
	$(INSTALL) -d "$(EXTENSION_DIR)"
	$(INSTALL) -m 0644 shell-command.ts "$(EXTENSION_DIR)/$(EXTENSION_NAME)"
	$(INSTALL) -d "$(BINDIR)"
	$(INSTALL) -m 0755 howcli "$(BINDIR)/$(CLI_NAME)"

uninstall:
	uv tool uninstall howcli-cache || true
	rm -f "$(EXTENSION_DIR)/$(EXTENSION_NAME)"
	rm -f "$(BINDIR)/$(CLI_NAME)"

check:
	test -f shell-command.ts
	grep -q "export default" shell-command.ts
	bash -n howcli
	uv run --project howcli-cache howcli-cache --help >/dev/null
