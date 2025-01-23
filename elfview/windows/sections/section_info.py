from elfview.util.curses import Attrs, Colors, Position
from elfview.util.hexdump import hexdump_line, hexdump_get_full_size
from elfview.ui import Pad, Finder, Scroller, Table
from elfview import config

PAD_Y_SIZE_OFFSET = 1


class SectionInfoPad(Pad):
    NAME = 'SectionInfo'

    def __init__(self):
        super().__init__()
        self.y_offset = 4

        self.finder = Finder()

        self.last_win_dimensions = self.dimensions

    def calculate_dimensions(self, win_dimensions):
        self.dimensions.y, self.dimensions.x = win_dimensions.y - PAD_Y_SIZE_OFFSET, win_dimensions.x // 2
        self.last_win_dimensions = win_dimensions

    def refresh(self, pad, win_dimensions):
        pad.refresh(
            0, 0,
            config.WINDOW_SWITCH_BAR_SIZE, win_dimensions.x // 2,
            win_dimensions.y, win_dimensions.x - 1
        )

    def render(self, win, pad):
        if win.get_pad('SectionsList').vertical_pos_updated:
            self.cursor_y = 0
            self.scroll_y = 0
            if config.RESET_FINDER_ON_LINKED_PAD_CHANGE:
                self.finder.reset()

        pad.border()

        with Attrs(pad, [Colors.INVERSE.color()], win.current_pad == 1) as _:
            pad_title = ' Section '
            pad.addstr(0, win.get_current_pad().dimensions.x//2 - len(pad_title)//2, pad_title)

        sections = list(win.app.file.sections)

        section_idx = win.get_pad('SectionsList').cursor_y + win.get_pad('SectionsList').scroll_y

        if section_idx >= len(sections):
            return

        section = win.app.file.sections[section_idx]

        hexdump_line_bytes_size = self.dimensions.x // config.HEXDUMP_WIDTH_TO_BYTE_SIZE_COEFFICIENT

        self.finder.find_if_requested(
            self,
            hexdump_get_full_size(section.hexdump, hexdump_line_bytes_size),
            lambda i: hexdump_line(section.hexdump, i, hexdump_line_bytes_size),
            self.last_win_dimensions.x // 2
        )

        self.max_y_size = len(section.hexdump) - 1

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
            hexdump_get_full_size(section.hexdump, hexdump_line_bytes_size),
            lambda i: hexdump_line(section.hexdump, i, hexdump_line_bytes_size),
            offset,
        )

    def process_input(self, ch):
        super().process_input(ch)
        self.finder.process_input(self, ch, self.last_win_dimensions.x // 2)
