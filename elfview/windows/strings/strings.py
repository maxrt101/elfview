from elfview.util.curses import Attrs, Colors, Position
from elfview.ui import Pad, Finder, Scroller, ColoredTable
from elfview import config
from functools import reduce
import curses

PAD_Y_SIZE_OFFSET = 1


class StringListPad(Pad):
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
            win_dimensions.y - PAD_Y_SIZE_OFFSET, win_dimensions.x
        )

    def render(self, win, pad):
        pad.border()

        with Attrs(pad, [Colors.INVERSE.color()], win.current_pad == 0) as _:
            pad_title = ' Strings '
            pad.addstr(0, win.get_current_pad().dimensions.x//2 - len(pad_title)//2, pad_title)

        self.finder.find_if_requested(
            self,
            len(win.app.file.strings),
            lambda i: win.app.file.strings[i][1]
        )

        self.max_y_size = len(win.app.file.strings) - 1

        max_str_len = reduce(lambda v, e: max(v, len(e[1])), win.app.file.strings, 0)

        offset = Position(3, 3)

        table = ColoredTable({
            'Offset': [10, [curses.A_BOLD]],
            'Name': [max_str_len, []]
        })

        table.header['Name'][0] = min(
            max_str_len,
            (
                self.dimensions.x - 2 - offset.x -
                reduce(lambda v, e: v + e[0], [v for k, v in table.header.items() if k != 'Name'], 0)
            )
        )

        table.render_header(pad, Position(offset.y - 1, offset.x))

        def get_str(i: int):
            return table.get_line_str({
                'Offset': f'0x{win.app.file.strings[i][0]:06x}',
                'Name': f'{win.app.file.strings[i][1]}',
            })

        Scroller.finder_aware_scroll(
            self,
            pad,
            len(win.app.file.strings),
            get_str,
            offset
        )

    def process_input(self, ch):
        super().process_input(ch)
        self.finder.process_input(self, ch)