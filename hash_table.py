from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


RESIZE_DOUBLE = 1
RESIZE_ADD_10000 = 2


@dataclass
class HashTable:
    initial_size: int
    max_load_factor: float
    resize_strategy: int
    table: List[Optional[str]] = field(init=False)
    count: int = field(default=0, init=False)
    resize_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.initial_size <= 0:
            raise ValueError("initial_size must be positive")
        if not 0 < self.max_load_factor <= 1:
            raise ValueError("max_load_factor must be between 0 and 1")
        if self.resize_strategy not in {RESIZE_DOUBLE, RESIZE_ADD_10000}:
            raise ValueError("resize_strategy must be 1 (double) or 2 (add 10000)")
        self.table = [None] * self.initial_size

    @property
    def size(self) -> int:
        return len(self.table)

    def _index_for(self, value: str, table_size: Optional[int] = None) -> int:
        size = self.size if table_size is None else table_size
        return hash(value) % size

    def _needs_resize(self) -> bool:
        if self.count == 0:
            return False
        return (self.count / self.size) >= self.max_load_factor

    def _next_size(self) -> int:
        if self.resize_strategy == RESIZE_DOUBLE:
            return self.size * 2
        return self.size + 10000

    def _insert_into_table(self, value: str, table: List[Optional[str]]) -> bool:
        size = len(table)
        index = self._index_for(value, size)

        for _ in range(size):
            current = table[index]
            if current is None:
                table[index] = value
                return True
            if current == value:
                return False
            index = (index + 1) % size

        raise RuntimeError("hash table is full")

    def _rehash(self) -> None:
        new_table: List[Optional[str]] = [None] * self._next_size()
        for value in self.table:
            if value is not None:
                self._insert_into_table(value, new_table)
        self.table = new_table
        self.resize_count += 1

    def insert(self, string_to_insert: str) -> None:
        inserted = self._insert_into_table(string_to_insert, self.table)
        if not inserted:
            return

        self.count += 1
        if self._needs_resize():
            self._rehash()

    def find(self, string_to_find: str) -> bool:
        index = self._index_for(string_to_find)

        for _ in range(self.size):
            current = self.table[index]
            if current is None:
                return False
            if current == string_to_find:
                return True
            index = (index + 1) % self.size

        return False
