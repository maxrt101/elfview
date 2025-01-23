from elfview.util.curses import Attrs, Colors, Position
from elfview.ui import Pad, Finder, Scroller, Table
from elfview import config
from functools import reduce

PAD_Y_SIZE_OFFSET = 1


class SectionsListPad(Pad):
    NAME = 'SectionsList'

    def __init__(self):
        super().__init__()
        self.y_offset = 3

        self.finder = Finder()

    def calculate_dimensions(self, win_dimensions):
        self.dimensions.y, self.dimensions.x = win_dimensions.y - PAD_Y_SIZE_OFFSET, win_dimensions.x // 2

    def refresh(self, pad, win_dimensions):
        pad.refresh(
            0, 0,
            config.WINDOW_SWITCH_BAR_SIZE, 0,
            win_dimensions.y - PAD_Y_SIZE_OFFSET, win_dimensions.x // 2
        )

    def render(self, win, pad):
        pad.border()

        with Attrs(pad, [Colors.INVERSE.color()], win.current_pad == 0) as _:
            pad_title = ' Sections List '
            pad.addstr(0, win.get_current_pad().dimensions.x//2 - len(pad_title)//2, pad_title)

        self.finder.find_if_requested(
            self,
            len(win.app.file.sections),
            lambda i: str(win.app.file.sections[i].name)
        )

        self.max_y_size = len(win.app.file.sections) - 1

        max_name_len = reduce(lambda v, e: max(v, len(e.name)), win.app.file.sections, 0)

        offset = Position(2, 3)

        table = Table({
            'Name': max_name_len,
            'Type': 10,
            'Offset': 10,
            'Size': 10,
            'Flags': 8,
            'Align': 5
        })

        table.header['Name'] = min(
            max_name_len,
            (
                self.dimensions.x - 2 - offset.x -
                reduce(lambda v, e: v + e, [v for k, v in table.header.items() if k != 'Name'], 0)
            )
        )

        table.render_header(pad, Position(offset.y - 1, offset.x))

        def get_str(i: int) -> str:
            return table.get_line_str({
                'Name': win.app.file.sections[i].name[:table.header['Name']-1],
                'Type': win.app.file.sections[i].type_name,
                'Offset': f'0x{win.app.file.sections[i].offset:x}',
                'Size': f'0x{win.app.file.sections[i].size:x}',
                'Flags': f'0x{win.app.file.sections[i].flags:x}',
                'Align': f'{win.app.file.sections[i].align}'
            })

        Scroller.finder_aware_scroll(
            self,
            pad,
            len(win.app.file.sections),
            get_str,
            offset
        )

    def process_input(self, ch):
        super().process_input(ch)
        self.finder.process_input(self, ch)
