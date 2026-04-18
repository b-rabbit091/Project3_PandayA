from __future__ import annotations

from hash_table import HashTable, RESIZE_ADD_10000, RESIZE_DOUBLE


def make_values(prefix: str, count: int) -> list[str]:
    return [f"{prefix}_{i}" for i in range(count)]


def test_add_five_and_search() -> None:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_DOUBLE)
    present = make_values("present", 5)
    missing = make_values("missing", 5)

    for value in present:
        table.insert(value)

    assert all(table.find(value) for value in present)
    assert all(not table.find(value) for value in missing)


def test_23_values_double_strategy_resizes_once() -> None:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_DOUBLE)
    values = make_values("double23", 23)

    for value in values:
        table.insert(value)

    assert table.resize_count == 1
    assert table.size == 32
    assert all(table.find(value) for value in values)


def test_24_values_double_strategy_resizes_twice() -> None:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_DOUBLE)
    values = make_values("double24", 24)

    for value in values:
        table.insert(value)

    assert table.resize_count == 2
    assert table.size == 64
    assert all(table.find(value) for value in values)


def test_23_values_add_strategy_correct_size() -> None:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_ADD_10000)
    values = make_values("add23", 23)

    for value in values:
        table.insert(value)

    assert table.resize_count == 1
    assert table.size == 10016
    assert all(table.find(value) for value in values)


def test_24_values_add_strategy_correct_size() -> None:
    table = HashTable(initial_size=16, max_load_factor=0.75, resize_strategy=RESIZE_ADD_10000)
    values = make_values("add24", 24)

    for value in values:
        table.insert(value)

    assert table.resize_count == 1
    assert table.size == 10016
    assert all(table.find(value) for value in values)
