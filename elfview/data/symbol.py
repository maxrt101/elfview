from dataclasses import dataclass


@dataclass
class Symbol:
    name: str
    type_name: str
    value: int
    size: int
    binding: str
    visibility: str
