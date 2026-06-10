PREFIX ?= $(HOME)
BINDIR ?= $(PREFIX)/bin
DATADIR ?= $(PREFIX)/share/gread
INSTALL ?= install

.PHONY: install uninstall check

install:
	$(INSTALL) -d "$(BINDIR)"
	$(INSTALL) -m 0755 gread "$(BINDIR)/gread"
	$(INSTALL) -d "$(DATADIR)/excludes"
	$(INSTALL) -m 0644 excludes/*.txt "$(DATADIR)/excludes/"
	cp -r package.json src tsconfig.json node_modules "$(DATADIR)/"

uninstall:
	rm -f "$(BINDIR)/gread"
	rm -rf "$(DATADIR)"

check:
	npx tsc --noEmit
