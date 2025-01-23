from enum import Enum
import curses

# What library to use as backend for ELF/Dwarf parsing (elftools/lief)
BACKEND = 'elftools'

# Create colorful hexdump if True
USE_COLORFUL_HEXDUMP = True

# Generate hexdump lines on need-to-render basis
# If False, will generate hexdump for each section and whole file on startup
DEFER_HEXDUMP_GENERATION = True

# Resets finder (search) if linked pad (e.g. Functions/Variable is linked to File List)
# has changed selected element (e.g. next file)
RESET_FINDER_ON_LINKED_PAD_CHANGE = False

# Search through full buffer, however long it may be
# If False, will use area [cursor-SEARCH_REACH:cursor+SEARCH_REACH] form buffer
SEARCH_WHOLE_BUFFER = True

# Negative and positive offset used to retrieve searchable sub buffer
SEARCH_REACH = 32

# Use KEY_FIND_NEXT/KEY_FIND_PREV to select next/prev occurrence
# Has the same value as SEARCH_WHOLE_BUFFER because it works strangely
# with limited buffer
SEARCH_USE_NEXT_OCCURRENCE = SEARCH_WHOLE_BUFFER

# Turns on debug features
DEBUG = False

# Use strings extracted from .strtab & .dynstr, it's the 'right' way to do this
# If set to False, will scan ELF contents for char sequences with min length of DEFAULT_STRING_MIN_LENGTH
USE_STRINGS_FROM_SECTIONS = True

# Default length for sequence of chars to be considered a string
# Used when USE_STRINGS_FROM_SECTIONS is False
DEFAULT_STRING_MIN_LENGTH = 15

# How much lines/elements is skipped when scrolling up/down with KEY_SCROLL_SKIP_UP/KEY_SCROLL_SKIP_DOWN
PAGE_SCROLL_SKIP_SIZE = 16

# Size (height) of top bar (window switch)
WINDOW_SWITCH_BAR_SIZE = 3

# Size of Info pad in Files window
FILES_WINDOW_INFO_PAD_SIZE = 10

# Coefficient of screen width to byte size (line_size)
HEXDUMP_WIDTH_TO_BYTE_SIZE_COEFFICIENT = 5

# TODO: SymbolMap (if terminal can only use ASCII chars)
# horizontal = "─"
# vertical = "│"
# top_left = "┌"
# top_right = "┐"
# bottom_left = "└"
# bottom_right = "┘"


class KeyMap(Enum):
    KEY_ENTER = ord('\n')
    KEY_ESCAPE = 27
    KEY_BACKSPACE = 127
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_LEFT = curses.KEY_LEFT
    KEY_RIGHT = curses.KEY_RIGHT
    KEY_SWITCH_WINDOW = ord('\t')
    KEY_SCROLL_SKIP_UP = ord('[')
    KEY_SCROLL_SKIP_DOWN = ord(']')
    KEY_FIND = ord('/')
    KEY_FIND_NEXT = ord('n')
    KEY_FIND_PREV = ord('p')
    KEY_FILTER = ord('f')


class ColorMap(Enum):
    DEFAULT = (curses.COLOR_WHITE, curses.COLOR_BLACK)
    INVERSE = (curses.COLOR_BLACK, curses.COLOR_WHITE)
    HIGHLIGHT = (curses.COLOR_YELLOW, curses.COLOR_BLACK)
    ALERT = (curses.COLOR_WHITE, curses.COLOR_RED)
    FUNCTION = (curses.COLOR_CYAN, curses.COLOR_BLACK)
    VARIABLE = (curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    TYPE_NAME = (curses.COLOR_YELLOW, curses.COLOR_BLACK)
    TYPE_CONST = (curses.COLOR_CYAN, curses.COLOR_BLACK)
    TYPE_VOLATILE = (curses.COLOR_CYAN, curses.COLOR_BLACK)
    TYPE_POINTER = (curses.COLOR_GREEN, curses.COLOR_BLACK)
    TYPE_DIMENSIONS = (curses.COLOR_GREEN, curses.COLOR_BLACK)
    FIND_OCCURRENCE_HIGHLIGHT = (curses.COLOR_BLACK, curses.COLOR_YELLOW)
