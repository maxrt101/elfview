from elfview.util.curses import Position, Colors, Attrs, CursorState
from elfview import config
import curses


def prompt_bar(title: str, dimensions: Position, x_offset: int = 0) -> str:
    size = Position(3, dimensions.x - 6)
    pad = curses.newpad(size.y, size.x)

    with Attrs(pad, [Colors.INVERSE.color()]) as _:
        pad.border()
        pad.addstr(1, 1, title)

    CursorState.HIGH_VISIBILITY.set()

    # TODO: ?
    curses.noecho()
    # curses.echo()

    pad.refresh(
        0, 0,
        dimensions.y // 2, x_offset + 2,
        dimensions.y // 2 + size.y, x_offset + size.x + 1
    )

    input_str = ''
    i = 0

    with Attrs(pad, [curses.A_BLINK]) as _:
        while len(input_str) < size.x:
            ch = pad.getch()

            if ch == config.KeyMap.KEY_ENTER.value:
                break
            elif ch == config.KeyMap.KEY_BACKSPACE.value:
                # TODO: Check if this is needed
                if len(input_str) > 0:
                    input_str = input_str[:len(input_str)-1]
            elif ch == config.KeyMap.KEY_ESCAPE.value:
                return ''
            else:
                input_str += chr(ch)

            pad.addstr(1, 1 + len(title), input_str + ' ')
            pad.move(1, 1 + len(title) + len(input_str))

            i += 1

            pad.refresh(
                0, 0,
                dimensions.y // 2, x_offset + 2,
                dimensions.y // 2 + size.y, x_offset + size.x + 1
            )

    curses.noecho()
    CursorState.INVISIBLE.set()

    return input_str
