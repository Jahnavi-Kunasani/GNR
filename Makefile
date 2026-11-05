# GNR401 Spatial-Domain Image Enhancement
# Run these targets from the project root with: make <target>

PYTHON ?= python3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python
STAMP := $(VENV)/.installed

.PHONY: help setup check prepare point histogram filters sharpening run all clean

help:
	@echo "Available commands:"
	@echo "  make setup       Create the virtual environment and install dependencies"
	@echo "  make check       Check that each scene has four aligned JP2 bands"
	@echo "  make prepare     Create multispectral TIFF and TCC/FCC previews"
	@echo "  make point       Run point-operation enhancement methods"
	@echo "  make histogram   Run histogram enhancement methods"
	@echo "  make filters     Run spatial filtering methods"
	@echo "  make sharpening  Run sharpening and edge-enhancement methods"
	@echo "  make run         Run the complete pipeline in the correct order"
	@echo "  make clean       Remove generated processed data and result files"

setup: $(STAMP)

$(STAMP): requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt
	@touch $(STAMP)

check: setup
	$(VENV_PYTHON) src/01_check_data.py

prepare: setup
	$(VENV_PYTHON) src/02_prepare_data.py

point: setup
	$(VENV_PYTHON) src/03_point_operations.py

histogram: setup
	$(VENV_PYTHON) src/04_histogram_operations.py

filters: setup
	$(VENV_PYTHON) src/05_spatial_filters.py

sharpening: setup
	$(VENV_PYTHON) src/06_sharpening.py

# Keep this recipe sequential: each stage uses the output of the previous stage.
run: setup
	$(VENV_PYTHON) src/01_check_data.py && \
	$(VENV_PYTHON) src/02_prepare_data.py && \
	$(VENV_PYTHON) src/03_point_operations.py && \
	$(VENV_PYTHON) src/04_histogram_operations.py && \
	$(VENV_PYTHON) src/05_spatial_filters.py && \
	$(VENV_PYTHON) src/06_sharpening.py

all: run

clean:
	rm -rf data/processed/* results/point_operations/* results/histogram_operations/* results/spatial_filters/* results/sharpening/*
