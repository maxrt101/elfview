from elfview.util.curses import Position, Colors, Attrs
from functools import reduce
import curses


def alert(lines: list[str], dimensions: Position, x_offset: int = 0) -> str:
    max_line_size = reduce(lambda v, e: max(v, len(e)), lines, 0)
    size = Position(2 + len(lines), min(dimensions.x - 6, max_line_size + 4))
    pad = curses.newpad(size.y, size.x)

    with Attrs(pad, [Colors.ALERT.color()]) as _:
        pad.border()
        y = 1
        for line in lines:
            pad.addstr(y, 1, f' {line} ')
            y += 1

    pad.refresh(
        0, 0,
        dimensions.y // 2, dimensions.x // 2 - size.x//2 + x_offset,
        dimensions.y // 2 + size.y, dimensions.x // 2 + size.x + x_offset + 1
    )

    pad.getch()
