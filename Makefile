# AI-KIT front-door. Requires GNU Make; each target maps to the canonical Python command.
TARGET ?=
TASK ?=
TITLE ?=
MSG ?=
RECORD ?=
AGENT ?=
TASKS ?=
OUTPUT ?=
EXPERIMENT ?=

.PHONY: check test wheel install apply doctor context adapters retire route configure providers measure metrics analyze scaffold evaluate adr changelog

check:
	python scripts/check_kit.py

test:
	python -m unittest discover -s tests -v

wheel:
	python -m pip wheel . --no-deps --wheel-dir dist
	python tests/wheel_smoke.py dist

install:
	python scripts/install.py $(TARGET)

apply:
	python scripts/install.py $(TARGET) --apply

doctor:
	python scripts/doctor.py $(TARGET)

context:
	python scripts/context.py snapshot $(TARGET)

adapters:
	python scripts/adapters.py report --project $(TARGET)

retire:
	python scripts/adapters.py retire $(TARGET) --agent $(AGENT)

route:
	python scripts/router.py route "$(TASK)"

configure:
	python scripts/router.py configure $(TARGET) --apply

providers:
	python scripts/router.py providers

measure:
	python scripts/metrics.py record $(TARGET) --from-json $(RECORD)

metrics:
	python scripts/metrics.py summary $(TARGET)

analyze:
	python scripts/metrics.py analyze $(TARGET)

scaffold:
	python scripts/evaluate.py scaffold --output $(OUTPUT) --experiment $(EXPERIMENT) --task $(TASK)

evaluate:
	python scripts/evaluate.py coverage $(TARGET) --tasks $(TASKS)

adr:
	python scripts/adr.py new "$(TITLE)"

changelog:
	python scripts/changelog.py add "$(MSG)"
