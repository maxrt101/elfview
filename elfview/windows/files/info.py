from elfview.util.curses import Attrs, Colors, Position
from elfview.ui import Pad, MultiAttrString
from functools import reduce
from elfview import config
import curses

PAD_Y_SIZE_OFFSET = 1


class InfoPad(Pad):
    NAME = 'Info'

    def __init__(self):
        super().__init__()
        self.y_offset = 3

    def calculate_dimensions(self, win_dimensions):
        self.dimensions.y, self.dimensions.x = config.FILES_WINDOW_INFO_PAD_SIZE, win_dimensions.x // 2

    def refresh(self, pad, win_dimensions):
        pad.refresh(
            0, 0,
            win_dimensions.y - config.FILES_WINDOW_INFO_PAD_SIZE - 1, win_dimensions.x // 2,
            win_dimensions.y - 1, win_dimensions.x - 1
        )

    def render(self, win, pad):
        pad.border()

        # TODO: Maybe, if selected, expand the window and show more info about selected function

        with Attrs(pad, [Colors.INVERSE.color()], win.current_pad == 2) as _:
            pad_title = ' Info '
            pad.addstr(0, self.dimensions.x // 2 - len(pad_title) // 2, pad_title)

        index = win.get_pad('Files').cursor_y + win.get_pad('Files').scroll_y

        if index < len(win.app.compilation_units_order):
            filename = win.app.compilation_units_order[index]
            file_fn_size = win.app.compilation_units[filename].functions_size
            file_var_size = win.app.compilation_units[filename].variables_size
        else:
            file_fn_size = '?'
            file_var_size = '?'

        MultiAttrString([
            ('Filters: "', []),
            (','.join(win.get_pad('Files').filters), [curses.A_BOLD]),
            ('"', []),
        ]).render(self, pad, Position(1, 2))

        MultiAttrString([
            ('File Functions Size:  ', []),
            (f'{file_fn_size}', [curses.A_BOLD]),
        ]).render(self, pad, Position(2, 2))

        MultiAttrString([
            ('File Variable Size:   ', []),
            (f'{file_var_size}', [curses.A_BOLD]),
        ]).render(self, pad, Position(3, 2))

        MultiAttrString([
            ('Total Functions Size: ', []),
            (f'{reduce(lambda v, e: v + e.functions_size, win.app.compilation_units.values(), 0)}', [curses.A_BOLD]),
        ]).render(self, pad, Position(4, 2))

        MultiAttrString([
            ('Total Variable Size:  ', []),
            (f'{reduce(lambda v, e: v + e.variables_size, win.app.compilation_units.values(), 0)}', [curses.A_BOLD]),
        ]).render(self, pad, Position(5, 2))
