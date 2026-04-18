from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from hash_table import HashTable, RESIZE_ADD_10000, RESIZE_DOUBLE


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str


def make_values(prefix: str, count: int) -> list[str]:
    return [f"{prefix}_{i}" for i in range(count)]


def run_check(name: str, check: Callable[[], str]) -> CheckResult:
    try:
        details = check()
        return CheckResult(name=name, passed=True, details=details)
    except AssertionError as error:
        message = str(error) if str(error) else "assertion failed"
        return CheckResult(name=name, passed=False, details=message)


def check_add_five_and_search() -> str:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_DOUBLE)
    present = make_values("present", 5)
    missing = make_values("missing", 5)

    for value in present:
        table.insert(value)

    assert all(table.find(value) for value in present), "not all inserted values were found"
    assert all(not table.find(value) for value in missing), "a missing value was reported as present"
    return "Inserted 5 strings, found all 5, and rejected 5 different strings."


def check_23_double() -> str:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_DOUBLE)
    values = make_values("double23", 23)

    for value in values:
        table.insert(value)

    assert table.resize_count == 1, f"expected 1 resize, got {table.resize_count}"
    assert table.size == 32, f"expected final size 32, got {table.size}"
    assert all(table.find(value) for value in values), "not all 23 values were found after resizing"
    return "23 values with doubling caused 1 resize and a final table size of 32."


def check_24_double() -> str:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_DOUBLE)
    values = make_values("double24", 24)

    for value in values:
        table.insert(value)

    assert table.resize_count == 2, f"expected 2 resizes, got {table.resize_count}"
    assert table.size == 64, f"expected final size 64, got {table.size}"
    assert all(table.find(value) for value in values), "not all 24 values were found after resizing"
    return "24 values with doubling caused 2 resizes and a final table size of 64."


def check_23_add() -> str:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_ADD_10000)
    values = make_values("add23", 23)

    for value in values:
        table.insert(value)

    assert table.resize_count == 1, f"expected 1 resize, got {table.resize_count}"
    assert table.size == 10016, f"expected final size 10016, got {table.size}"
    assert all(table.find(value) for value in values), "not all 23 values were found after resizing"
    return "23 values with +10000 resizing caused 1 resize and a final table size of 10016."


def check_24_add() -> str:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_ADD_10000)
    values = make_values("add24", 24)

    for value in values:
        table.insert(value)

    assert table.resize_count == 1, f"expected 1 resize, got {table.resize_count}"
    assert table.size == 10016, f"expected final size 10016, got {table.size}"
    assert all(table.find(value) for value in values), "not all 24 values were found after resizing"
    return "24 values with +10000 resizing caused 1 resize and a final table size of 10016."


def main() -> None:
    checks: List[tuple[str, Callable[[], str]]] = [
        ("Part 1", check_add_five_and_search),
        ("Part 2", check_23_double),
        ("Part 3", check_24_double),
        ("Part 4", check_23_add),
        ("Part 5", check_24_add),
    ]

    results = [run_check(name, check) for name, check in checks]
    passed = sum(result.passed for result in results)

    print("Hash Table Correctness Checks")
    print("=============================")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{result.name}: {status}")
        print(f"  {result.details}")
    print("=============================")
    print(f"Passed {passed} of {len(results)} checks.")


if __name__ == "__main__":
    main()
