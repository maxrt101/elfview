from elfview.util.curses import Position
from elfview.data import File
from elfview import config
from typing import Any


def lief_parse(filepath: str, dimensions: Position) -> tuple[File, Any]:
    from .lief import parse
    return parse(filepath, dimensions)


def elftools_parse(filepath: str, dimensions: Position) -> tuple[File, Any]:
    from .elftools import parse
    return parse(filepath, dimensions)


def parse(filepath: str, dimensions: Position, backend: str = config.BACKEND) -> tuple[File, Any]:
    backends = {
        'lief': lief_parse,
        'elftools': elftools_parse
    }

    if backend in backends:
        return backends[backend](filepath, dimensions)

    raise ValueError(f'Invalid backend {backend}')
