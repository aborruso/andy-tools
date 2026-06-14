PREFIX ?= $(HOME)
BINDIR ?= $(PREFIX)/bin
INSTALL ?= install

.PHONY: install uninstall check

install:
	$(INSTALL) -d "$(BINDIR)"
	$(INSTALL) -m 0755 esearch "$(BINDIR)/esearch"

uninstall:
	rm -f "$(BINDIR)/esearch"

check:
	bash -n esearch
