from elfview.util.curses import Position, Attrs
from .multi_attr_str import MultiAttrString
import curses


class Table:
    def __init__(self, header: dict[str, int]):
        self.header = header

    def get_header_str(self) -> str:
        return ''.join([k + ' ' * (v - len(k)) for k, v in self.header.items()])

    def get_line_str(self, values: dict[str, str]) -> str:
        return ''.join([v + ' ' * (self.header[k] - len(v)) for k, v in values.items()])

    def render_header(self, pad, pos: Position, attrs=[curses.A_BOLD]):
        with Attrs(pad, attrs) as _:
            pad.addstr(pos.y, pos.x, self.get_header_str())

    def render_line(self, pad, pos: Position, values: dict[str, str], attrs=[curses.A_BOLD]):
        with Attrs(pad, attrs) as _:
            pad.addstr(pos.y, pos.x, self.get_line_str(values))


class ColoredTable:
    HeaderElement = tuple[int, list[int]] | list[int, list[int]]

    def __init__(self, header: dict[str, HeaderElement]):
        self.header = header

    def get_header_str(self) -> str:
        # FIXME: Why -1 ?
        return ' '.join([k + ' ' * (v[0] - len(k) - 1) for k, v in self.header.items()])

    def get_line_str(self, values: dict[str, str]) -> MultiAttrString:
        pairs = []

        for k, v in values.items():
            pairs.append((v[:self.header[k][0]] + ' ' * (self.header[k][0] - len(v)), self.header[k][1]))

        return MultiAttrString(pairs)

    def render_header(self, pad, pos: Position, attrs=[curses.A_BOLD]):
        with Attrs(pad, attrs) as _:
            pad.addstr(pos.y, pos.x, self.get_header_str())

    def render_line(self, ui_pad, curses_pad, pos: Position, values: dict[str, str]):
        self.get_line_str(values).render(ui_pad, curses_pad, pos)
