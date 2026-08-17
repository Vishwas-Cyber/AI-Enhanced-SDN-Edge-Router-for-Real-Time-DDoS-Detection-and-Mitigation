.PHONY: install test lint compile dashboard check

install:
	python -m pip install -r requirements.txt

test:
	python -m pytest

compile:
	python -m py_compile dashboard/app.py src/controller/monitor.py src/runtime_contract.py

check: compile test

dashboard:
	streamlit run dashboard/app.py
