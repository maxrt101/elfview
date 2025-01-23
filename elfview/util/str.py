from datetime import datetime
import string


def bytes_size_to_str(num: int, suffix: str = 'B') -> str:
    for unit in ('', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi'):
        if abs(num) < 1024.0:
            return f'{num:3.1f}{unit}{suffix}'
        num /= 1024.0
    return f'{num:.1f}Yi{suffix}'


def timestamp_to_str(ts) -> str:
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def is_printable(b) -> bool:
    return chr(b) in string.printable


def count_digits(n):
    # TODO: Use more efficient way to count digits
    return len(str(n))


def format_escape_codes(s: str) -> str:
    escape_code_map = {
        '\r': '\\r',
        '\n': '\\n',
        '\b': '\\b',
        '\t': '\\t',
    }

    result = ''
    for c in s:
        if c in escape_code_map:
            result += escape_code_map[c]
        else:
            result += c

    return result
