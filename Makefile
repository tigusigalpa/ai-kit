# AI-KIT front-door. Requires GNU Make; each target maps to the canonical Python command.
TARGET ?=
TASK ?=
TITLE ?=
MSG ?=
RECORD ?=

.PHONY: check test install apply doctor route configure measure metrics adr changelog

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

measure:
	python scripts/metrics.py record $(TARGET) --from-json $(RECORD)

metrics:
	python scripts/metrics.py summary $(TARGET)

adr:
	python scripts/adr.py new "$(TITLE)"

changelog:
	python scripts/changelog.py add "$(MSG)"
