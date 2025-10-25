# 🧩 Assignment 6 – Modular Financial Analytics and Trading Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![OOP Patterns](https://img.shields.io/badge/Design%20Patterns-Factory%2C%20Singleton%2C%20Builder%2C%20Decorator%2C%20Adapter%2C%20Composite%2C%20Strategy%2C%20Observer%2C%20Command-orange.svg)]()
[![Tests](https://img.shields.io/badge/tests-pytest-green.svg)]()

A modular Python system for simulating a **financial analytics and trading platform**, designed to apply key **object-oriented design patterns**.  
This project demonstrates how creational, structural, and behavioral patterns enhance **modularity, reusability, and maintainability** in finance-related software.

---

## 📖 Overview

This system models a simplified financial trading and analytics engine, capable of:
- Loading instruments and market data from multiple external sources.
- Constructing hierarchical portfolios.
- Generating and executing trading signals.
- Performing analytics such as volatility, beta, and drawdown.
- Reporting trade outcomes and performance.

It integrates **creational**, **structural**, and **behavioral** design patterns to simulate a real-world trading platform architecture.

---

## 🎯 Learning Objectives

- Implement **creational patterns** to manage object creation and configuration.  
- Apply **structural patterns** for flexible composition and integration.  
- Use **behavioral patterns** to encapsulate dynamic behavior and event-driven logic.  
- Analyze tradeoffs between complexity, performance, and maintainability.  
- Integrate all patterns into a cohesive, extensible financial system.  

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/assignment-6.git
cd assignment-6
```
### 2. Install dependencies
```bash
pip install pandas numpy matplotlib pytest
```
### 3. Verify setup
```bash
python main.py
```

## 🧾 Configuration

This project loads configuration and parameters from several files that define runtime behavior, strategy settings, and portfolio composition.

| File | Purpose |
|------|----------|
| `config.json` | Global configuration shared across modules via Singleton pattern |
| `strategy_params.json` | Defines thresholds and parameters for different trading strategies |
| `portfolio_structure.json` | Describes hierarchical portfolio setup used by the Builder and Composite patterns |
| `external_data_yahoo.json`, `external_data_bloomberg.xml` | Mock data adapters for Yahoo and Bloomberg formats |
| `instruments.csv`, `market_data.csv` | Sample local data for instruments and price history |

## 🧩 Module Descriptions

| File / Directory | Design Pattern(s) Implemented | Description |
|------------------|-------------------------------|--------------|
| `patterns/factory.py` | **Factory Pattern** | Creates instrument objects (`Stock`, `Bond`, `ETF`) dynamically from `instruments.csv`. Demonstrates how the Factory centralizes object instantiation logic. |
| `patterns/singleton.py` | **Singleton Pattern** | Manages a single shared configuration instance loaded from `config.json`. Ensures consistent global access across modules. |
| `patterns/builder.py` | **Builder Pattern**, **Composite Pattern** | Constructs hierarchical portfolio objects from `portfolio_structure.json`. Supports nested sub-portfolios and recursive aggregation of values. |
| `patterns/decorator.py` | **Decorator Pattern** | Extends base instrument analytics by adding additional metrics (`Volatility`, `Beta`, `Drawdown`) without modifying core classes. Demonstrates decorator stacking. |
| `patterns/adapter.py` | **Adapter Pattern** | Translates external data from `external_data_yahoo.json` and `external_data_bloomberg.xml` into unified internal `MarketDataPoint` objects. |
| `patterns/strategy.py` | **Strategy Pattern** | Defines interchangeable trading strategies (`MeanReversionStrategy`, `BreakoutStrategy`). Each implements its own `generate_signals()` method using parameters from `strategy_params.json`. |
| `patterns/observer.py` | **Observer Pattern** | Implements a publish-subscribe mechanism where observers (e.g., `LoggerObserver`, `AlertObserver`) react dynamically when trading signals are generated. |
| `patterns/command.py` | **Command Pattern** | Encapsulates trade execution logic and provides undo/redo functionality. Used by the `CommandInvoker` to manage trade lifecycle operations. |
| `data_loader.py` | **Adapter Pattern** | Coordinates data ingestion from multiple sources and standardizes them into a consistent format for downstream analytics. |
| `analytics.py` | **Decorator Pattern** | Provides analytics computations such as volatility, beta, and drawdown. Demonstrates extending core instrument analytics using decorators. |
| `engine.py` | **Strategy, Observer, Command Patterns** | The central orchestrator of the system — executes strategies, triggers observers, and handles command-based trade execution and reversal. |
| `models.py` | **Factory, Composite Patterns** | Defines financial instruments, positions, and portfolio components. Provides interfaces for `Instrument`, `Position`, and composite portfolio nodes. |
| `reporting.py` | **Observer Pattern** | Logs signal events, system status, and analytics results through observer callbacks. Supports multiple reporting channels. |
| `main.py` | **Integration Layer** | Entry point of the application. Loads configuration, initializes data ingestion, applies selected strategies, and generates reports. |
| `tests/` | — | Unit tests verifying correct behavior of each design pattern implementation. Includes tests for Factory, Singleton, Strategy, Observer, and Command. |
| `design_report.md` | — | Written summary documenting the design rationale, tradeoffs, and integration of all patterns used in this project. |
| `README.md` | — | Provides setup instructions, configuration details, and module descriptions (this file). |

---

Each module corresponds directly to a **design pattern** taught in this assignment.  
Together, they form a cohesive, modular financial analytics system that supports:
- Extensible strategy design  
- Dynamic behavior encapsulation  
- Clear separation of concerns  
- Reusable component architecture



