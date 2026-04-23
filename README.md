# Project 3: Grad Amortized Analysis and Hashing

## Environment
- Language/version: Python 3.11
- IDE: PyCharm
- Required packages: None

## How To Run
1. Open a terminal in this repository.
2. Run `python run_checks.py` to execute the required correctness checks.
3. Run `python milestone2.py` to generate the Milestone 2 data files and graphs.
4. If `python` is not available on your PATH in Windows, either install Python 3.11+ or run the script with a full Python executable path.
5. Optional: run `python -m pytest -q` to execute the automated test file if you have `pytest` installed.

No extra setup is required beyond having Python installed.

## Hashing
This project implements a hash table that stores strings and resolves collisions using linear probing.

- The constructor accepts an initial table size, a maximum load factor, and a resize strategy.
- The hash table uses Python's built-in `hash()` function and maps values into the table with modulo arithmetic.
- `insert(string_to_insert)` adds a string only if it is not already present.
- `find(string_to_find)` returns `True` when the string exists and `False` otherwise.
- When collisions happen, the table checks the next slot linearly and wraps around with modulo arithmetic.
- When the load factor reaches the configured limit, the table resizes and rehashes all stored strings into the new array.
- Resize strategy `1` doubles the table size.
- Resize strategy `2` adds `10000` to the current table size.

This implementation triggers a resize when the load factor reaches the limit, not only when it goes above the limit.

## Files
- `hash_table.py`: Hash table implementation.
- `test_hash_table.py`: Automated correctness tests.
- `run_checks.py`: Command-line runner that prints the required check results.
- `milestone2.py`: Milestone 2 dataset generation, timing analysis, and graph generation.
- `milestone2_outputs/`: Generated timing tables and graph images for Milestone 2.
