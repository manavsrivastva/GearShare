# GearShare - Equipment Rental Management System

## Project Overview
GearShare is a Python equipment rental management system using OOP, DSA, SQLite and SQL.

## Technologies
- Python 3
- SQLite
- SQL
- Pytest
- Git

## Features

### Object-Oriented Programming
- Abstract classes for gear items and customers.
- Equipment, accessories and display-only items.
- Basic, Plus and Pro membership tiers.
- Custom exceptions and rental business rules.

### Data Structures and Algorithms
- Linear and binary search.
- Bubble, insertion and selection sort.
- Hash-based SKU detection.
- FIFO waiting queues.
- Rental history and undo using a stack.
- Recursive category traversal.
- Performance benchmarking.

### Database
- SQLite relational database.
- Normalization up to 3NF.
- Primary and foreign keys, UNIQUE and CHECK constraints.
- CSV database seeding.
- Parameterized SQL queries.
- Transactions and rollback.
- SQL injection demonstration.
- Composite indexes.

## Project Structure
- data/ - CSV source data
- dsa/ - Data structures and algorithms
- storage/ - SQLite integration
- tests/ - Pytest test cases
- docs/ - Project documentation
- items.py, customers.py, rentals.py - Core models
- gearshare.py - Application logic
- main.py - Application entry point
- schema.sql - Database schema
- benchmark.py - Performance benchmarks
- injection_demo.py - SQL injection demonstration
- index_demo.py - Index execution plan comparison
- DECISIONS.md - Technical decisions

## Installation

Create a virtual environment:

    python -m venv .venv

Activate it in PowerShell:

    .\.venv\Scripts\Activate.ps1

Install dependencies:

    pip install -r requirements.txt

## Running the Application

    python main.py

## Running Tests

    python -m pytest -v

Latest verification: 59 tests passed.

## SQL Injection Demonstration

    python injection_demo.py

## Database Indexing

    python index_demo.py

Both indexes were verified using SQLite EXPLAIN QUERY PLAN.

## Documentation
The docs folder contains:
- Flat-file analysis
- Normalization report
- ER diagram
- Benchmark report and results
- Database indexing report

## Conclusion
GearShare demonstrates practical Python OOP, DSA, relational database design, SQL transactions and performance optimization.
