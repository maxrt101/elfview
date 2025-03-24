from elfview.util.curses import Position, Attrs, Colors, CursorState, set_stdscr
from elfview.backends import parse
from elfview import windows
from elfview import config
import curses


class ELFViewApp:
    BLOCK = '█'

    def __init__(
            self,
            stdscr,
            filename: str,
            file_prefixes: list[str] = [],
            backend: str = config.BACKEND):
        self.stdscr = stdscr
        self.should_run = True

        set_stdscr(stdscr)

        # TODO: Remove, already exists in File.filepath
        self.filename = filename
        # TODO: Rename file_prefix -> remove_file_prefix
        self.file_prefixes = file_prefixes

        self.dimensions = Position(curses.LINES, curses.COLS)
        self.center = Position(self.dimensions.y // 2, self.dimensions.x // 2)

        Colors.init()

        CursorState.INVISIBLE.set()

        self.current_window = 0

        self.windows = windows.create(self)

        self.file, self.backend_handle = parse(filename, self.dimensions, backend if backend else config.BACKEND)
        self.compilation_units = None
        self.compilation_units_order = None

    def cleanup(self):
        curses.nocbreak()
        curses.echo()
        self.stdscr.keypad(False)
        CursorState.NORMAL.set()

    def __process_input(self, ch):
        if ch == ord('q'):
            self.should_run = False
            return

        if ch == ord('\t'):
            self.current_window += 1

        if self.current_window >= len(self.windows):
            self.current_window = 0

        self.get_current_window().process_input(ch)

    def get_current_window(self):
        return self.windows[self.current_window]

    def run(self):
        try:
            while self.should_run:
                self.dimensions.y, self.dimensions.x = self.stdscr.getmaxyx()
                self.center = Position(self.dimensions.y // 2, self.dimensions.x // 2)

                # Window Bar
                window_bar_pad = curses.newpad(3, self.dimensions.x)
                window_bar_pad.border()
                prev_x = 2
                for i in range(len(self.windows)):
                    with Attrs(window_bar_pad, [Colors.INVERSE.color()], i == self.current_window) as _:
                        window_bar_pad.addstr(1, prev_x, self.windows[i].name)

                    prev_x += len(self.windows[i].name)

                    if i + 1 < len(self.windows):
                        window_bar_pad.addstr(1, prev_x, ' │ ')

                    prev_x += 3

                window_bar_pad.refresh(
                    0, 0,
                    0, 0,
                    config.WINDOW_SWITCH_BAR_SIZE, self.dimensions.x - 1
                )

                for pad in self.get_current_window().pads:
                    pad.calculate_dimensions(Position(self.dimensions.y - 3, self.dimensions.x))
                    curses_pad = curses.newpad(pad.dimensions.y, pad.dimensions.x)
                    pad.render(self.get_current_window(), curses_pad)
                    pad.refresh(curses_pad, self.dimensions)

                if config.DEBUG:
                    with Attrs(self.stdscr, [Colors.DEFAULT.color(), curses.A_BOLD]) as _:
                        pos_str = f'{self.current_window} {self.get_current_window().current_pad}'
                        self.stdscr.addstr(0, 0, pos_str)

                # Status Bar
                with Attrs(self.stdscr, [Colors.INVERSE.color()]) as _:
                    status_bar_str = 'Press \'q\' to exit | Press <TAB> to change window | Press <LEFT>/<RIGHT> to change subwindows'

                    self.stdscr.addstr(self.dimensions.y-1, 0, status_bar_str)
                    self.stdscr.addstr(self.dimensions.y-1, len(status_bar_str), " " * (self.dimensions.x - len(status_bar_str) - 1))

                # Refresh screen
                self.stdscr.refresh()

                # Disable line buffering & echoing, enable special key processing
                # FIXME: This is a workaround, if done at initialization, stops working
                curses.cbreak()
                curses.noecho()
                self.stdscr.keypad(True)

                # Process input
                self.__process_input(self.stdscr.getch())

        except KeyboardInterrupt:
            return
