# Makefile for Parcl Buyer Intelligence Platform

.PHONY: help install test lint format clean run-pipeline run-api run-web run-streamlit reproduce

help:
	@echo "Available commands:"
	@echo "  make install         Install Python and Node dependencies"
	@echo "  make test            Execute pytest test suite"
	@echo "  make lint            Run ruff and mypy"
	@echo "  make run-pipeline    Execute end-to-end ML & analytics pipeline"
	@echo "  make run-api         Start FastAPI backend server"
	@echo "  make run-web         Start React Vite development server"
	@echo "  make run-streamlit   Start Streamlit dashboard"
	@echo "  make reproduce       Clean, rebuild data, models, metrics from raw CSV"

install:
	pip install -e packages/core
	cd apps/web && npm install

test:
	python -m pytest packages/core/tests -v

lint:
	ruff check packages/core apps/api
	mypy packages/core apps/api

run-pipeline:
	python -m parcl_core.pipeline --phase 1

run-api:
	uvicorn apps.api.main:app --reload --port 8000

run-web:
	cd apps/web && npm run dev

run-streamlit:
	streamlit run apps/streamlit/app.py

reproduce:
	python -m parcl_core.pipeline --phase 1
