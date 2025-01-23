from elfview.util.curses import Position, Colors, CondAttrs
from .multi_attr_str import MultiAttrString


class Scroller:
    @staticmethod
    def scroll(ui_pad, curses_pad, collection_len, get_str, offset: Position = Position(0, 0), attrs=[]):
        y = 0
        y_offset = offset.y
        x_offset = offset.x

        for i in range(ui_pad.scroll_y, collection_len):
            with CondAttrs(curses_pad, [
                *[a(y, i) for a in attrs],
                (y == ui_pad.cursor_y, [Colors.INVERSE.color()])
            ]) as _:
                line = get_str(i)
                if type(line) is str:
                    curses_pad.addstr(
                        y + y_offset,
                        x_offset,
                        line[:min(len(line), ui_pad.dimensions.x - x_offset - 1)]
                    )
                elif type(line) is MultiAttrString:
                    line.render(ui_pad, curses_pad, Position(y + y_offset, x_offset), y == ui_pad.cursor_y)
                else:
                    raise ValueError('Invalid type for line (scroll line render)')

            y += 1
            if y >= ui_pad.dimensions.y - y_offset - 1:
                break

    @staticmethod
    def finder_aware_scroll(ui_pad, curses_pad, collection_len, get_str, offset: Position = Position(0, 0), attrs=[]):
        if attrs is None:
            attrs = list()
        y = 0
        y_offset = offset.y
        x_offset = offset.x

        for i in range(ui_pad.scroll_y, collection_len):
            line = get_str(i)

            with CondAttrs(curses_pad, [
                *[a(y, i) for a in attrs],
                (ui_pad.finder.verify(line), [Colors.FIND_OCCURRENCE_HIGHLIGHT.color()]),
                (y == ui_pad.cursor_y, [Colors.INVERSE.color()])
            ]):
                if type(line) is str:
                    curses_pad.addstr(
                        y + y_offset,
                        x_offset,
                        line[:min(len(line), ui_pad.dimensions.x - x_offset - 1)]
                    )
                elif type(line) is MultiAttrString:
                    line.render(ui_pad, curses_pad, Position(y + y_offset, x_offset), y == ui_pad.cursor_y or ui_pad.finder.verify(line))
                else:
                    raise ValueError(f'Invalid type ({type(line)}) for line (scroll line render)')

            y += 1
            if y >= ui_pad.dimensions.y - y_offset - 1:
                break


