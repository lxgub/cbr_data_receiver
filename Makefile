SERVICE=cbr_data_receiver
PYTHONBASE=python3.8

ifndef ($(CONFIG))
CONFIG=local
endif

.PHONY:
help:
	@echo ""
	@echo "Help:"
	@echo ""
	@echo "**Install project**:"
	@echo "    make install"
	@echo ""
	@echo "Start API:"
	@echo "    make start"
	@echo ""
		@echo ""
	@echo "Tests:"
	@echo "    make tests"
	@echo ""

.PHONY:
install:
	${PYTHONBASE} -m venv env
	@. env/bin/activate; \
	pip install --upgrade pip; \
	python setup.py install; \
    $(SERVICE)_setconfiguration; \
    deactivate

.PHONY:
migrations:
	@. env/bin/activate; \
    $(SERVICE)_runmigrations; \
    deactivate

.PHONY:
tests:
	@. env/bin/activate; \
	pytest

.PHONY:
start:
	@. env/bin/activate; \
	$(SERVICE)


