# AI-KIT front-door. Requires GNU Make; each target maps to the canonical Python command.
TARGET ?=
TASK ?=
TITLE ?=
MSG ?=

.PHONY: check test install apply doctor route configure adr changelog

check:
	python scripts/check_kit.py

test:
	python -m unittest discover -s tests -v

install:
	python scripts/install.py $(TARGET)

apply:
	python scripts/install.py $(TARGET) --apply

doctor:
	python scripts/doctor.py $(TARGET)

route:
	python scripts/router.py route "$(TASK)"

configure:
	python scripts/router.py configure $(TARGET) --apply

adr:
	python scripts/adr.py new "$(TITLE)"

changelog:
	python scripts/changelog.py add "$(MSG)"
