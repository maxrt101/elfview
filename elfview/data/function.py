from dataclasses import dataclass
from elfview.ui.multi_attr_str import MultiAttrString
from elfview.util.curses import Colors
from .type import Type


@dataclass
class Function:
    name: str
    return_type: Type
    args: list
    size: int

    def get_multi_attr_str(self) -> MultiAttrString:
        pairs = [
            *self.return_type.get_multi_attr_str_pairs(),
            (self.name, [Colors.FUNCTION.color()]),
            ('(', [Colors.FUNCTION.color()])
        ]

        for arg in self.args:
            # If type is missing (e.g. variadic function last param), don't add it
            if arg[0]:
                pairs.extend(arg[0].get_multi_attr_str_pairs())
            pairs.append((arg[1], [Colors.FUNCTION.color()]))
            if arg != self.args[-1]:
                pairs.append((', ', [Colors.FUNCTION.color()]))

        pairs.append((')', [Colors.FUNCTION.color()]))

        return MultiAttrString(pairs)

    def __str__(self):
        return f'{self.return_type} {self.name}({", ".join([f"{t} {a}" for t, a in self.args])})'
