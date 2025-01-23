from dataclasses import dataclass


@dataclass
class Section:
    name: str
    type_name: str
    addr: int
    offset: int
    size: int
    flags: int
    align: int
    # TODO: store list[int] (or bytes) if config.DONT_STORE_HEXDUMP
    hexdump: list[str]
