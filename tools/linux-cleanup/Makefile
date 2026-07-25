PREFIX ?= $(HOME)
BINDIR ?= $(PREFIX)/bin
INSTALL ?= install

.PHONY: install uninstall check

install:
	$(INSTALL) -d "$(BINDIR)"
	$(INSTALL) -m 0755 linux-cleanup.sh "$(BINDIR)/linux-cleanup"

uninstall:
	rm -f "$(BINDIR)/linux-cleanup"

check:
	bash -n linux-cleanup.sh
