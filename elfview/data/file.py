from dataclasses import dataclass
from elfview.data.cu import CompilationUnit
from elfview.data.symbol import Symbol
from elfview.data.section import Section


@dataclass
class File:
    path: str
    name: str
    size: int
    created: str
    modified: str
    accessed: str
    file_type: str
    machine: str
    abi: str
    flags: list[str]
    entrypoint: tuple[int, str]
    compilation_units: dict[str, CompilationUnit]
    sections: list[Section]
    symbols: list[Symbol]
    strings: list[tuple[int, str]]
    # TODO: store list[int] (or bytes) if config.DONT_STORE_HEXDUMP
    hexdump: list[str]
