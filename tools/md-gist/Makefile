PREFIX ?= $(HOME)
BINDIR ?= $(PREFIX)/bin
INSTALL ?= install

.PHONY: install uninstall check

install:
	$(INSTALL) -d "$(BINDIR)"
	$(INSTALL) -m 0755 md-gist "$(BINDIR)/md-gist"

uninstall:
	rm -f "$(BINDIR)/md-gist"

check:
	bash -n md-gist
