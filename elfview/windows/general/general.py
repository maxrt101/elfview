from elfview.util.str import bytes_size_to_str, timestamp_to_str
from elfview.util.curses import Attrs, Colors
from elfview.util.logo import LOGO
from elfview.ui import Pad
from elfview import config
from functools import reduce
import curses


PAD_Y_SIZE_OFFSET = 1


class GeneralInfoPad(Pad):
    NAME = 'General'

    def __init__(self):
        super().__init__()
        self.y_offset = 3

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
            with Attrs(pad, [curses.A_BOLD]) as _:
                pad_title = ' ELFView '
                pad.addstr(0, win.get_current_pad().dimensions.x//2 - len(pad_title)//2, pad_title)

        logo_lines = LOGO.split('\n')
        max_logo_line_size = max([len(l) for l in logo_lines])

        logo_y = 2
        with Attrs(pad, [curses.A_BOLD]) as _:
            for line in logo_lines:
                pad.addstr(logo_y, self.dimensions.x//2 - max_logo_line_size//2, line)
                logo_y += 1

        file_info = {
            'Name': win.app.file.name,
            'Size': '{} ({} bytes)'.format(bytes_size_to_str(win.app.file.size), win.app.file.size),
            'Created': win.app.file.created,
            'Modified': win.app.file.modified,
            'Accessed': win.app.file.accessed,
            # TODO: stat()
            'File Type': win.app.file.file_type,
            'Machine': win.app.file.machine,
            'ABI': win.app.file.abi,
            'Flags': ', '.join(win.app.file.flags),
            'Entrypoint': f'0x{win.app.file.entrypoint[0]:x} ({win.app.file.entrypoint[1]})',
        }

        max_left_col_size = reduce(lambda v, e: max(v, len(e)), file_info.keys(), 0)
        max_file_info_line_size = reduce(lambda v, e: max(v, len(e) + len(file_info[e])), file_info.keys(), 0)

        info_y = 0
        info_y_offset = 2 + len(logo_lines) + 2

        for key, val in file_info.items():
            with Attrs(pad, [Colors.DEFAULT.color()]) as _:
                file_info_text = '{}:{} {}'.format(key, ' ' * (max_left_col_size - len(key)), val)
                pad.addstr(
                    info_y + info_y_offset,
                    win.get_current_pad().dimensions.x//2 - max_file_info_line_size//2,
                    file_info_text
                )
            info_y += 1
