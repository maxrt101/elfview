from elfview.util.curses import Attrs, Colors, Position
from elfview.util.str import count_digits
from elfview.ui import Pad, Finder, Scroller, MultiAttrString, prompt_bar
from elfview import config
import curses

PAD_Y_SIZE_OFFSET = 1


class FilesPad(Pad):
    NAME = 'Files'

    def __init__(self):
        super().__init__()
        self.y_offset = 3

        self.filters = []
        self.should_update_filter = True

        self.finder = Finder()

        self.max_file_size_digits = 4

    def calculate_dimensions(self, win_dimensions):
        self.dimensions.y, self.dimensions.x = win_dimensions.y - PAD_Y_SIZE_OFFSET, win_dimensions.x // 2

    def refresh(self, pad, win_dimensions):
        pad.refresh(
            0, 0,
            config.WINDOW_SWITCH_BAR_SIZE, 0,
            win_dimensions.y - PAD_Y_SIZE_OFFSET, win_dimensions.x // 2
        )

    def __prepare_files(self, win):
        win.app.compilation_units = {k: v for k, v in win.app.file.compilation_units.items() if any(f in k for f in self.filters)} if self.filters else win.app.file.compilation_units

        cu_sizes = list()

        for name, cu in win.app.compilation_units.items():
            cu_sizes.append((name, cu.functions_size + cu.variables_size))
            self.max_file_size_digits = max(self.max_file_size_digits, count_digits(cu.functions_size + cu.variables_size))

        cu_sizes = sorted(cu_sizes, key=lambda x: x[1], reverse=True)
        win.app.compilation_units_order = [k[0] for k in cu_sizes]

    def render(self, win, pad):
        pad.border()

        with Attrs(pad, [Colors.INVERSE.color()], win.current_pad == 0) as _:
            pad_title = ' Files '
            pad.addstr(0, self.dimensions.x//2 - len(pad_title)//2, pad_title)

        if win.app.compilation_units is None or self.should_update_filter:
            self.__prepare_files(win)
            self.should_update_filter = False
            self.cursor_y = 0
            self.vertical_pos_updated = True

        self.finder.find_if_requested(
            self,
            len(win.app.compilation_units_order),
            lambda i: str(win.app.compilation_units_order[i])
        )

        self.max_y_size = len(win.app.compilation_units_order) - 1

        def get_str(i: int) -> MultiAttrString:
            cu_name = win.app.compilation_units_order[i]
            cu_size = win.app.compilation_units[cu_name].functions_size + win.app.compilation_units[cu_name].variables_size
            for prefix in win.app.file_prefixes:
                cu_name = cu_name.removeprefix(prefix)
            return MultiAttrString([
                ('{{:0{}}}'.format(self.max_file_size_digits).format(cu_size), [curses.A_BOLD]),
                (' │ ' + cu_name, [])
            ])

        Scroller.finder_aware_scroll(
            self,
            pad,
            len(win.app.compilation_units_order),
            get_str,
            Position(2, 2)
        )

    def process_input(self, ch):
        super().process_input(ch)
        if ch == config.KeyMap.KEY_FILTER.value:
            self.filters = prompt_bar('Filter: ', self.dimensions).split(',')
            self.should_update_filter = True
        self.finder.process_input(self, ch)
