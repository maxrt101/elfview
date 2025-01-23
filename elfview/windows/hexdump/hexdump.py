from elfview.util.curses import Attrs, Colors, Position
from elfview.util.hexdump import hexdump_line
from elfview.ui import Pad, Finder, Scroller, Table
from elfview import config

PAD_Y_SIZE_OFFSET = 1


class HexdumpPad(Pad):
    def __init__(self):
        super().__init__()
        self.y_offset = 4

        self.finder = Finder()

    def calculate_dimensions(self, win_dimensions):
        self.dimensions.y, self.dimensions.x = win_dimensions.y - PAD_Y_SIZE_OFFSET, win_dimensions.x

    def refresh(self, pad, win_dimensions):
        pad.refresh(
            0, 0,
            config.WINDOW_SWITCH_BAR_SIZE, 0,
            win_dimensions.y, win_dimensions.x - 1
        )

    def render(self, win, pad):
        pad.border()

        with Attrs(pad, [Colors.INVERSE.color()], win.current_pad == 0) as _:
            pad_title = ' Hexdump '
            pad.addstr(0, win.get_current_pad().dimensions.x//2 - len(pad_title)//2, pad_title)

        self.finder.find_if_requested(
            self,
            len(win.app.file.hexdump),
            lambda i: str(win.app.file.hexdump[i])
        )

        self.max_y_size = len(win.app.file.hexdump) - 1

        line_size = self.dimensions.x // config.HEXDUMP_WIDTH_TO_BYTE_SIZE_COEFFICIENT

        offset = Position(3, 3)

        table = Table({
            'Addr': 8,
            'Hex': line_size * 3 + 4,
            'ASCII': line_size
        })

        table.render_header(pad, Position(offset.y - 1, offset.x))

        Scroller.finder_aware_scroll(
            self,
            pad,
            len(win.app.file.hexdump),
            lambda i: hexdump_line(win.app.file.hexdump, i, line_size),
            offset,
        )

    def process_input(self, ch):
        super().process_input(ch)
        self.finder.process_input(self, ch)

