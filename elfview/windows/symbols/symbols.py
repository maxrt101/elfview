from elfview.util.curses import Attrs, Colors, Position
from elfview.ui import Pad, Finder, Scroller, Table
from elfview import config
from functools import reduce

PAD_Y_SIZE_OFFSET = 1


class SymbolsListPad(Pad):
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
            pad_title = ' Symbols '
            pad.addstr(0, win.get_current_pad().dimensions.x//2 - len(pad_title)//2, pad_title)

        symbols = list(win.app.file.symbols)

        max_name_len = reduce(lambda v, e: max(v, len(e.name)), symbols, 0)

        self.finder.find_if_requested(
            self,
            len(symbols),
            lambda i: str(symbols[i].name)
        )

        self.max_y_size = len(symbols) - 1

        offset = Position(3, 3)

        table = Table({
            'Name': max_name_len,
            'Type': 16,
            'Value': 16,
            'Size': 16,
            'Bind': 16,
            'Vis': 16
        })

        # Cap name to the space left when taking into account all other fields
        table.header['Name'] = min(max_name_len, self.dimensions.x - 2 - offset.x - reduce(lambda v, e: v + e, [v for k, v in table.header.items() if k != 'Name'], 0))

        table.render_header(pad, Position(offset.y - 1, offset.x))

        def get_str(i: int) -> str:
            return table.get_line_str({
                'Name': symbols[i].name[:min(table.header['Name'], len(symbols[i].name))],
                'Type': symbols[i].type_name,
                'Value': f'0x{symbols[i].value:x}',
                'Size': str(symbols[i].size),
                'Bind': symbols[i].binding,
                'Vis': symbols[i].visibility
            })

        Scroller.finder_aware_scroll(
            self,
            pad,
            len(symbols),
            get_str,
            offset
        )

    def process_input(self, ch):
        super().process_input(ch)
        self.finder.process_input(self, ch)
