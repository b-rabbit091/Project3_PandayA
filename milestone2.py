from __future__ import annotations

import csv
import math
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from hash_table import HashTable, RESIZE_ADD_10000, RESIZE_DOUBLE

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as error:  # pragma: no cover
    raise SystemExit(
        "matplotlib is required to generate the Milestone 2 graphs. "
        "Install it with 'python -m pip install matplotlib'."
    ) from error


DATASET_SIZE = 131_072
RANDOM_SEED = 20260423
OUTPUT_DIR = Path("milestone2_outputs")
REHASH_TIMING_FILE = OUTPUT_DIR / "rehash_timings.txt"
LOAD_FACTOR_TIMING_FILE = OUTPUT_DIR / "load_factor_timings.txt"
REHASH_PLOT_FILE = OUTPUT_DIR / "rehash_cost.png"
TIME_SUCC_PLOT_FILE = OUTPUT_DIR / "time_succ.png"
TIME_FAIL_PLOT_FILE = OUTPUT_DIR / "time_fail.png"
REPEATS = 5
SEARCH_SAMPLES = 2_000


@dataclass(frozen=True)
class Dataset:
    whole_list: list[str]
    add_values: list[str]
    check_values: list[str]


@dataclass(frozen=True)
class RehashTimingRow:
    q: int
    values_inserted: int
    no_rehash_time_ns: float
    no_rehash_time_per_insert_ns: float
    doubling_time_ns: float
    doubling_time_per_insert_ns: float
    add_10000_time_ns: float
    add_10000_time_per_insert_ns: float


@dataclass(frozen=True)
class LoadFactorTimingRow:
    load_factor: float
    values_in_table: int
    successful_time_ns: float
    unsuccessful_time_ns: float


def create_dataset(size: int = DATASET_SIZE, seed: int = RANDOM_SEED) -> Dataset:
    if size % 2 != 0:
        raise ValueError("dataset size must be even")

    generator = random.Random(seed)
    sampled_numbers = generator.sample(range(10_000_000, 100_000_000), size)
    whole_list = [f"{value:08d}" for value in sampled_numbers]

    if len(whole_list) != len(set(whole_list)):
        raise ValueError("dataset contains duplicate values")

    midpoint = size // 2
    return Dataset(
        whole_list=whole_list,
        add_values=whole_list[:midpoint],
        check_values=whole_list[midpoint:],
    )


def insertion_count_for_q(q: int) -> int:
    return ((3 * (2**q)) // 4) - 1


def time_insertions(
    values: list[str],
    initial_size: int,
    max_load_factor: float,
    resize_strategy: int,
    repeats: int = REPEATS,
) -> float:
    measurements: list[int] = []

    for _ in range(repeats):
        table = HashTable(
            initial_size=initial_size,
            max_load_factor=max_load_factor,
            resize_strategy=resize_strategy,
        )
        start = time.perf_counter_ns()
        for value in values:
            table.insert(value)
        measurements.append(time.perf_counter_ns() - start)

    return statistics.mean(measurements)


def generate_rehash_timings(dataset: Dataset) -> list[RehashTimingRow]:
    rows: list[RehashTimingRow] = []

    for q in range(4, 18):
        count = insertion_count_for_q(q)
        values = dataset.whole_list[:count]

        no_rehash_time_ns = time_insertions(
            values=values,
            initial_size=2**17,
            max_load_factor=0.75,
            resize_strategy=RESIZE_DOUBLE,
        )
        doubling_time_ns = time_insertions(
            values=values,
            initial_size=2**q,
            max_load_factor=0.75,
            resize_strategy=RESIZE_DOUBLE,
        )
        add_10000_time_ns = time_insertions(
            values=values,
            initial_size=2**q,
            max_load_factor=0.75,
            resize_strategy=RESIZE_ADD_10000,
        )

        rows.append(
            RehashTimingRow(
                q=q,
                values_inserted=count,
                no_rehash_time_ns=no_rehash_time_ns,
                no_rehash_time_per_insert_ns=no_rehash_time_ns / count,
                doubling_time_ns=doubling_time_ns,
                doubling_time_per_insert_ns=doubling_time_ns / count,
                add_10000_time_ns=add_10000_time_ns,
                add_10000_time_per_insert_ns=add_10000_time_ns / count,
            )
        )

    return rows


def build_load_factors() -> list[float]:
    load_factors = {round(step / 100, 2) for step in range(0, 100, 3)}
    load_factors.update({0.5, 0.99})
    return sorted(load_factors)


def average_search_time_ns(table: HashTable, values: Iterable[str]) -> float:
    total = 0
    count = 0

    for value in values:
        start = time.perf_counter_ns()
        table.find(value)
        total += time.perf_counter_ns() - start
        count += 1

    if count == 0:
        return 0.0
    return total / count


def generate_load_factor_timings(dataset: Dataset) -> list[LoadFactorTimingRow]:
    rows: list[LoadFactorTimingRow] = []
    capacity = 65_536

    for load_factor in build_load_factors():
        target_count = min(int(load_factor * capacity), len(dataset.add_values))
        table = HashTable(
            initial_size=capacity,
            max_load_factor=1.0,
            resize_strategy=RESIZE_DOUBLE,
        )

        for value in dataset.add_values[:target_count]:
            table.insert(value)

        successful_time_ns = average_search_time_ns(
            table,
            dataset.add_values[: min(target_count, SEARCH_SAMPLES)],
        )
        unsuccessful_time_ns = average_search_time_ns(
            table,
            dataset.check_values[:SEARCH_SAMPLES],
        )

        rows.append(
            LoadFactorTimingRow(
                load_factor=load_factor,
                values_in_table=target_count,
                successful_time_ns=successful_time_ns,
                unsuccessful_time_ns=unsuccessful_time_ns,
            )
        )

    return rows


def write_rehash_timings(rows: list[RehashTimingRow]) -> None:
    with REHASH_TIMING_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(
            [
                "q",
                "values_inserted",
                "no_rehash_time_ns",
                "no_rehash_time_per_insert_ns",
                "doubling_time_ns",
                "doubling_time_per_insert_ns",
                "add_10000_time_ns",
                "add_10000_time_per_insert_ns",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.q,
                    row.values_inserted,
                    f"{row.no_rehash_time_ns:.3f}",
                    f"{row.no_rehash_time_per_insert_ns:.6f}",
                    f"{row.doubling_time_ns:.3f}",
                    f"{row.doubling_time_per_insert_ns:.6f}",
                    f"{row.add_10000_time_ns:.3f}",
                    f"{row.add_10000_time_per_insert_ns:.6f}",
                ]
            )


def write_load_factor_timings(rows: list[LoadFactorTimingRow]) -> None:
    with LOAD_FACTOR_TIMING_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(
            [
                "load_factor",
                "values_in_table",
                "successful_time_ns",
                "unsuccessful_time_ns",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    f"{row.load_factor:.2f}",
                    row.values_in_table,
                    f"{row.successful_time_ns:.6f}",
                    f"{row.unsuccessful_time_ns:.6f}",
                ]
            )


def plot_rehash_timings(rows: list[RehashTimingRow]) -> None:
    q_values = [row.q for row in rows]
    plt.figure(figsize=(10, 6))
    plt.plot(
        q_values,
        [row.no_rehash_time_per_insert_ns for row in rows],
        marker="o",
        label="No Rehash",
    )
    plt.plot(
        q_values,
        [row.doubling_time_per_insert_ns for row in rows],
        marker="o",
        label="Rehashed (Doubling)",
    )
    plt.plot(
        q_values,
        [row.add_10000_time_per_insert_ns for row in rows],
        marker="o",
        label="Rehashed (Add 10000)",
    )
    plt.xlabel("q")
    plt.ylabel("Average insertion time (ns per inserted value)")
    plt.title("Rehash Cost vs q")
    plt.xticks(q_values)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(REHASH_PLOT_FILE, dpi=200)
    plt.close()


def linear_probes_success(load_factor: float) -> float:
    return 0.5 * (1 + (1 / (1 - load_factor)))


def linear_probes_fail(load_factor: float) -> float:
    return 0.5 * (1 + (1 / ((1 - load_factor) ** 2)))


def double_probes_success(load_factor: float) -> float:
    if load_factor == 0:
        return 1.0
    return -math.log(1 - load_factor) / load_factor


def double_probes_fail(load_factor: float) -> float:
    return 1 / (1 - load_factor)


def build_scaled_series(rows: list[LoadFactorTimingRow]) -> tuple[float, list[float], list[float]]:
    row_by_factor = {row.load_factor: row for row in rows}
    reference_factor = 0.5
    reference_row = row_by_factor[reference_factor]
    q_scale = linear_probes_success(reference_factor) / reference_row.successful_time_ns

    scaled_success = [q_scale * row.successful_time_ns for row in rows]
    scaled_fail = [q_scale * row.unsuccessful_time_ns for row in rows]
    return q_scale, scaled_success, scaled_fail


def plot_load_factor_timings(rows: list[LoadFactorTimingRow]) -> float:
    load_factors = [row.load_factor for row in rows]
    q_scale, scaled_success, scaled_fail = build_scaled_series(rows)

    success_theory_linear = [linear_probes_success(load_factor) for load_factor in load_factors]
    success_theory_double = [double_probes_success(load_factor) for load_factor in load_factors]
    fail_theory_linear = [linear_probes_fail(load_factor) for load_factor in load_factors]
    fail_theory_double = [double_probes_fail(load_factor) for load_factor in load_factors]

    plt.figure(figsize=(10, 6))
    plt.plot(load_factors, success_theory_linear, label="LinearProbsSucc(lambda)")
    plt.plot(load_factors, success_theory_double, label="DoubleProbsSucc(lambda)")
    plt.plot(load_factors, scaled_success, label="Q * LinearTimeSucc(lambda)")
    plt.xlabel("Load factor (lambda)")
    plt.ylabel("Average probes / scaled average time")
    plt.title("Successful Search Performance vs Load Factor")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(TIME_SUCC_PLOT_FILE, dpi=200)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.plot(load_factors, fail_theory_linear, label="LinearProbsFail(lambda)")
    plt.plot(load_factors, fail_theory_double, label="DoubleProbsFail(lambda)")
    plt.plot(load_factors, scaled_fail, label="Q * LinearTimeFail(lambda)")
    plt.xlabel("Load factor (lambda)")
    plt.ylabel("Average probes / scaled average time")
    plt.title("Unsuccessful Search Performance vs Load Factor")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(TIME_FAIL_PLOT_FILE, dpi=200)
    plt.close()

    return q_scale


def print_summary(
    dataset: Dataset,
    rehash_rows: list[RehashTimingRow],
    load_factor_rows: list[LoadFactorTimingRow],
    q_scale: float,
) -> None:
    print("Milestone 2 analysis complete.")
    print(f"wholeList size: {len(dataset.whole_list)}")
    print(f"addValues size: {len(dataset.add_values)}")
    print(f"checkValues size: {len(dataset.check_values)}")
    print("Verified dataset uniqueness: yes")
    print(f"Rehash timing rows: {len(rehash_rows)}")
    print(f"Load factor timing rows: {len(load_factor_rows)}")
    print(f"Scaling constant Q: {q_scale:.10f}")
    print(f"Saved {REHASH_TIMING_FILE}")
    print(f"Saved {LOAD_FACTOR_TIMING_FILE}")
    print(f"Saved {REHASH_PLOT_FILE}")
    print(f"Saved {TIME_SUCC_PLOT_FILE}")
    print(f"Saved {TIME_FAIL_PLOT_FILE}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    dataset = create_dataset()
    rehash_rows = generate_rehash_timings(dataset)
    load_factor_rows = generate_load_factor_timings(dataset)

    write_rehash_timings(rehash_rows)
    write_load_factor_timings(load_factor_rows)
    plot_rehash_timings(rehash_rows)
    q_scale = plot_load_factor_timings(load_factor_rows)

    print_summary(dataset, rehash_rows, load_factor_rows, q_scale)


if __name__ == "__main__":
    main()
