from dataclasses import dataclass
from enum import Enum
import elfview.config
import curses


CURSES_STDSCR = None


class Colors(Enum):
    DEFAULT = 1
    INVERSE = 2
    HIGHLIGHT = 3
    ALERT = 4
    FUNCTION = 5
    VARIABLE = 6
    TYPE_NAME = 7
    TYPE_CONST = 8
    TYPE_VOLATILE = 9
    TYPE_POINTER = 10
    TYPE_DIMENSIONS = 11
    FIND_OCCURRENCE_HIGHLIGHT = 12

    def color(self):
        return curses.color_pair(self.value)

    @staticmethod
    def init():
        for c in Colors:
            curses.init_pair(c.value, *getattr(elfview.config.ColorMap, c.name).value)


class CursorState(Enum):
    INVISIBLE = 0
    NORMAL = 1
    HIGH_VISIBILITY = 2

    def set(self):
        curses.curs_set(self.value)


class Attrs:
    def __init__(self, obj, attributes: list, cond: bool = True):
        self.obj = obj
        self.attributes = attributes
        self.cond = cond

    def __enter__(self):
        if self.cond:
            for attr in self.attributes:
                self.obj.attron(attr)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.cond:
            for attr in self.attributes:
                self.obj.attroff(attr)


class CondAttrs:
    def __init__(self, obj, attr_map: list[tuple[bool, list]]):
        self.obj = obj
        self.attr_map = attr_map

    def __enter__(self):
        for entry in self.attr_map:
            if entry[0]:
                for attr in entry[1]:
                    self.obj.attron(attr)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        for entry in self.attr_map[::-1]:
            if entry[0]:
                for attr in entry[1]:
                    self.obj.attroff(attr)


@dataclass
class Position:
    y: int = 0
    x: int = 0

    def cap(self, cap_y: tuple, cap_x: tuple):
        self.y = max(cap_y[0], self.y)
        self.y = min(cap_y[1]-1, self.y)
        self.x = max(cap_x[0], self.x)
        self.x = min(cap_x[1]-1, self.x)


def set_stdscr(stdscr):
    global CURSES_STDSCR
    CURSES_STDSCR = stdscr


def get_stdscr():
    return CURSES_STDSCR

