from dataclasses import dataclass
from elfview.util.curses import Attrs, Position


@dataclass
class MultiAttrString:
    # Pair of string, and it's attributes
    Pair = tuple[str, list[int]]

    pairs: list[Pair]

    def __str__(self):
        return ''.join([p[0] for p in self.pairs])

    def search(self, substr: str):
        return substr in str(self)

    def render(self, ui_pad, curses_pad, pos: Position, ignore_color: bool = False):
        x_offset = 0
        for pair in self.pairs:
            x_left = ui_pad.dimensions.x - (pos.x + x_offset) - 1
            with Attrs(curses_pad, pair[1], not ignore_color) as _:
                curses_pad.addstr(
                    pos.y,
                    pos.x + x_offset,
                    pair[0][:min(x_left, len(pair[0]))]
                )
            x_offset += len(pair[0])
            if pos.x + x_offset > ui_pad.dimensions.x - 1:
                return
