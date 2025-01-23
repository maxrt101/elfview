from elfview.ui import MultiAttrString
from elfview import config
import curses


HEXDUMP_DEFAULT_LINE_SIZE = 16


def __hexdump(data: list | bytes, line_size: int = 16) -> list[str]:
    result = []
    for i in range(0, len(data), line_size):
        line = '0x{:04X} │ '.format(i)
        hexs = ' '.join(['{:02X}'.format(n) for n in data[i:i+line_size+1]])
        # Align last line (which may not be divisible by line_size) to previous lines
        if len(hexs) < line_size * 3:
            hexs += ' ' * (line_size * 3 - len(hexs) + 2)
        line += hexs + ' │ '
        line += ''.join([chr(n) if chr(n).isprintable() else '.' for n in data[i:i+line_size+1]])
        result.append(line)
    return result


def __hexdump_colorful(data: list | bytes, line_size: int = HEXDUMP_DEFAULT_LINE_SIZE) -> list[MultiAttrString]:
    result = []
    for i in range(0, len(data), line_size):
        line = [('0x{:04X}'.format(i), [curses.A_BOLD])]
        hexs = ' '.join(['{:02X}'.format(n) for n in data[i:i+line_size+1]])
        # Align last line (which may not be divisible by line_size) to previous lines
        if len(hexs) < line_size * 3:
            hexs += ' ' * (line_size * 3 - len(hexs) + 2)
        hexs = ' │ ' + hexs + ' │ '
        line.append((hexs, []))
        line.append((''.join([chr(n) if chr(n).isprintable() else '.' for n in data[i:i+line_size+1]]), [curses.A_BOLD]))
        result.append(MultiAttrString(line))
    return result


def hexdump(data: list | bytes, line_size: int = HEXDUMP_DEFAULT_LINE_SIZE) ->  list[str | MultiAttrString]:
    return __hexdump_colorful(data, line_size) if config.USE_COLORFUL_HEXDUMP else __hexdump(data, line_size)


def hexdump_line(data: list | bytes, offset: int, line_size: int = HEXDUMP_DEFAULT_LINE_SIZE) -> str | MultiAttrString:
    if config.DEFER_HEXDUMP_GENERATION:
        return hexdump(data[offset * line_size:(offset+1) * line_size], line_size)[0]
    else:
        return str(data[offset])


def hexdump_lines(data: list | bytes, offset: int, count: int, line_size: int = HEXDUMP_DEFAULT_LINE_SIZE) -> list[str | MultiAttrString]:
    if config.DEFER_HEXDUMP_GENERATION:
        return hexdump(data[offset * line_size:(offset+count) * line_size], line_size)
    else:
        return data[offset:offset+count]


def hexdump_get_full_size(data: list | bytes, line_size: int = HEXDUMP_DEFAULT_LINE_SIZE) -> int:
    if config.DEFER_HEXDUMP_GENERATION:
        return len(data) // line_size
    else:
        return len(data)
