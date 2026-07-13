PREFIX ?= $(HOME)
BINDIR ?= $(PREFIX)/bin
DATADIR ?= $(PREFIX)/share/projump
INSTALL ?= install

.PHONY: install uninstall check deps

deps:
	npm install

install: deps
	$(INSTALL) -d "$(BINDIR)"
	$(INSTALL) -m 0755 projump-path "$(BINDIR)/projump-path"
	$(INSTALL) -d "$(DATADIR)"
	cp -r package.json package-lock.json src node_modules "$(DATADIR)/"

uninstall:
	rm -f "$(BINDIR)/projump-path"
	rm -rf "$(DATADIR)"

check:
	npm run check
