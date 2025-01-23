from elfview.util.curses import Attrs, Colors, Position
from elfview.data import Function, Variable
from elfview.util.str import count_digits
from elfview.ui import Pad, Finder, Scroller
from elfview import config

PAD_Y_SIZE_OFFSET = 1


class FuncsVarsPad(Pad):
    NAME = 'FnVar'

    def __init__(self):
        super().__init__()
        self.y_offset = 3

        self.finder = Finder()

        self.last_win_dimensions = self.dimensions

        self.max_file_size_digits = 4

    def calculate_dimensions(self, win_dimensions):
        self.dimensions.y, self.dimensions.x = win_dimensions.y - PAD_Y_SIZE_OFFSET - config.FILES_WINDOW_INFO_PAD_SIZE, win_dimensions.x // 2
        self.last_win_dimensions = win_dimensions

    def refresh(self, pad, win_dimensions):
        pad.refresh(
            0, 0,
            config.WINDOW_SWITCH_BAR_SIZE, win_dimensions.x // 2,
            win_dimensions.y - config.FILES_WINDOW_INFO_PAD_SIZE, win_dimensions.x - 1
        )

    def render(self, win, pad):
        if win.get_pad('Files').vertical_pos_updated:
            self.cursor_y = 0
            self.scroll_y = 0
            if config.RESET_FINDER_ON_LINKED_PAD_CHANGE:
                self.finder.reset()

        pad.border()

        # FIXME: DEBUG
        if config.DEBUG:
            pad.addstr(0, 0, f'{self.cursor_y} {self.scroll_y} {self.max_y_size}')

        with Attrs(pad, [Colors.INVERSE.color()], win.current_pad == 1) as _:
            pad_title = ' Functions/Variables '
            pad.addstr(0, self.dimensions.x // 2 - len(pad_title) // 2, pad_title)

        index = win.get_pad('Files').cursor_y + win.get_pad('Files').scroll_y

        if index >= len(win.app.compilation_units_order):
            return

        if win.app.compilation_units_order[index] not in win.app.compilation_units:
            return

        file = win.app.compilation_units[win.app.compilation_units_order[index]]

        functions_and_variables = file.functions + file.variables

        self.max_file_size_digits = max([
            self.max_file_size_digits,
            count_digits(file.functions[0].size) if len(file.functions) else 0,
            count_digits(file.variables[0].size) if len(file.variables) else 0
        ])

        self.finder.find_if_requested(
            self,
            len(functions_and_variables),
            lambda i: str(functions_and_variables[i].name),
            self.last_win_dimensions.x // 2
        )

        self.max_y_size = len(functions_and_variables) - 1

        def get_color(e):
            if type(e) is Function:
                return Colors.FUNCTION.color()
            elif type(e) is Variable:
                return Colors.VARIABLE.color()
            else:
                raise ValueError('Invalid element, expected Function or Variable')

        def get_str(i: int):
            element = functions_and_variables[i]
            multi_attr_str = element.get_multi_attr_str()
            multi_attr_str.pairs.insert(0, ('{{:0{}}} │ '.format(self.max_file_size_digits).format(element.size), [get_color(element)]))
            return multi_attr_str

        Scroller.finder_aware_scroll(
            self,
            pad,
            len(functions_and_variables),
            get_str,
            Position(2, 2),
            [
                lambda y, i: (type(functions_and_variables[i]) is Function, [Colors.FUNCTION.color()]),
                lambda y, i: (type(functions_and_variables[i]) is Variable, [Colors.VARIABLE.color()])
            ]
        )

    def process_input(self, ch):
        super().process_input(ch)
        self.finder.process_input(self, ch, self.last_win_dimensions.x // 2)
