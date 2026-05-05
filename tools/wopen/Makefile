PREFIX ?= $(HOME)
BINDIR ?= $(PREFIX)/bin
INSTALL ?= install

.PHONY: install uninstall check

install:
	$(INSTALL) -d "$(BINDIR)"
	$(INSTALL) -m 0755 wopen "$(BINDIR)/wopen"

uninstall:
	rm -f "$(BINDIR)/wopen"

check:
	bash -n wopen
