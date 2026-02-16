# Merchant Risk Assessment – BNPL Underwriting Pipeline
## Overview

This repository implements an end-to-end merchant risk assessment pipeline for BNPL (Buy Now Pay Later) underwriting use cases.

### The system:

- Ingests multi-source merchant data

- Normalizes inputs into structured underwriting-style features

- Computes dispute and counterparty risk using an interpretable scoring model

- Aggregates portfolio-level risk metrics

- Generates a concise LLM-based underwriting summary

The focus is on risk quantification, interpretability, and clean engineering practices.

## Risk Philosophy

### Risk is acceptable if it is priced — i.e., understood and quantified.

The pipeline models two primary exposures:

- Dispute Risk — probability of merchant-driven customer disputes and chargeback losses

- Counterparty Risk — exposure from merchant instability across the portfolio

The system is designed to measure and contextualize risk, not eliminate it.

## System Architecture
'''
Data Ingestion
    ↓
Feature Engineering
    ↓
Risk Scoring Model
    ↓
Portfolio Aggregation
    ↓
LLM Report Generation
'''

## Project Structure

model/        → Risk scoring logic
reporting/    → LLM-based underwriting summary
tests/        → Unit tests
data/         → Raw & processed data
main.py       → Pipeline entry point



## Data Pipeline

The pipeline simulates integration of five merchant data sources:

- Merchant metadata

- Transaction history

- Dispute records

- Portfolio-level aggregates

- Supporting documents (PDF processed asynchronously)

Engineering Principles

- Structured feature mapping

- Defensive null handling

- Idempotent pipeline execution

- Modular source integration

The design allows new data sources to be added without modifying scoring logic.

## Risk Model

The current implementation uses an interpretable heuristic scoring model:

- Baseline score: 50

- Risk adjustments based on feature signals

- Score bounded between 0–100

- Tier mapping: Low / Medium / High

The model emphasizes transparency and explainability.

### Target Definition (Production Context)

In a real BNPL system, the prediction target would typically be:

- Binary dispute occurrence

- Expected loss ratio

- Chargeback probability

- Merchant default likelihood

The current implementation simulates a structured risk scoring framework and is designed to be replaceable by:

- Logistic regression

- Gradient boosting

- Calibrated probabilistic classifiers

## Portfolio Aggregation

The system computes:

- Average portfolio risk probability

- Risk tier distribution

- Expected high-risk merchant count

This ensures underwriting decisions are evaluated within portfolio context rather than in isolation.

## LLM-Based Underwriting Report

A locally hosted transformer model generates a structured underwriting summary from:

- Merchant features

- Risk score and tier

- Portfolio-level metrics

- Feature importance (if available)

The LLM is used strictly for explanatory reporting.
It does not influence the underlying risk score or decision logic.

## Engineering & Governance Considerations

The repository demonstrates:

- Modular architecture

- Clear separation of concerns

- Unit testing via pytest

- Deterministic scoring logic

- Safe handling of missing inputs

In a production BNPL environment, additional controls would include:

- Input schema validation

- Probability calibration (Platt scaling / isotonic regression)

- Feature drift monitoring

- Score distribution tracking

- Model versioning & audit logging

- Human-in-the-loop approval workflows

The current design supports these extensions.


## Future Improvements

- Replace heuristic scoring with calibrated probabilistic model

- Introduce FastAPI service layer

- Containerize with Docker

- Add CI/CD validation

- Integrate real-time dispute feeds

## Purpose

This repository demonstrates:

- Risk modeling fundamentals

- Portfolio-aware underwriting logic

- LLM-assisted reporting

- Production-conscious ML engineering practices

The system is structured for clarity, extensibility, and governance alignment.