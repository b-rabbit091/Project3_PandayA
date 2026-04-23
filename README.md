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

## Conclusions

### A) Graphs and their character

The generated graphs are saved in `milestone2_outputs/rehash_cost.png`, `milestone2_outputs/time_succ.png`, and `milestone2_outputs/time_fail.png`.

The rehash-cost graph shows three curves plotted against `q`. The no-rehash curve is the most stable because the table starts at size `2^17`, so insertion mostly reflects ordinary hash-table work instead of resize overhead. The doubling and `add 10000` curves are less stable at smaller values of `q` because a resize happens sooner and the cost of reinserting old values is spread across fewer insertions. As `q` increases, all three curves become smoother and closer together.

The successful-search and failed-search graphs both increase as the load factor approaches `1.0`. The successful-search curve rises gradually at first and then climbs more noticeably near high load factors. The failed-search curve rises faster and becomes much steeper near the right side of the graph, which matches the expected behavior of linear probing when the table becomes crowded.

### B) Average time to add values under the two strategies

The average insertion time stays lowest and most predictable in the no-rehash case because the large initial table avoids nearly all resizing during the experiment. Between the two resize strategies, doubling usually gives more consistent long-run behavior because one resize creates a much larger amount of extra space. The `add 10000` strategy can look competitive at some smaller sizes, but as the number of insertions grows it tends to require more frequent future rehashes, which makes the average insertion cost less favorable over time.

### C) Strategy comparison with pros and cons

Doubling has the advantage of strong amortized performance. After a resize, the table has plenty of room, so future insertions remain efficient for longer. Its main drawback is that a resize is expensive when it happens because the whole table must be rebuilt into a much larger array, and memory usage jumps more sharply.

The `add 10000` strategy grows the table more gradually. That means each resize increases memory use by a smaller fixed amount, which can feel less aggressive. The drawback is that once the table becomes large, adding only `10000` extra slots may not provide enough new capacity, so rehashes can happen more often and total insertion cost can grow.

### D) Choosing the load factor

The timings for successful and failed searches suggest that the load factor should not be pushed too close to `1.0`. Search cost increases slowly at lower load factors, but once the table becomes crowded the unsuccessful-search cost rises very quickly. A practical choice is to keep the load factor somewhere around `0.5` to `0.75`, where memory use is still reasonable and search performance stays much more stable than it does near `0.9` or above.

### E) Match between linear probing theory and measured times

Yes, the measured results followed the same overall pattern predicted by linear probing theory. Successful searches became gradually slower as the load factor increased, while unsuccessful searches became much more expensive near high load factors. The exact measured times did not match the theoretical probe counts perfectly because timing includes constant overhead from Python execution, hashing, loop control, and system noise, but the shape of the curves matched the expected model.

### F) Surprising observations

One interesting result is that the `add 10000` strategy can appear fairly close to doubling for some smaller experiments even though doubling is usually the better long-term strategy. Another noticeable result is how sharply failed-search cost increases near a load factor of `1.0`; that makes it very clear why crowded linear-probing tables degrade so quickly. The most important takeaway is that average-case hash-table performance remains very good only while enough empty space is preserved.
