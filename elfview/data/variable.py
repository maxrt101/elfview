from dataclasses import dataclass
from elfview.ui.multi_attr_str import MultiAttrString
from elfview.util.curses import Colors
from .type import Type


@dataclass
class Variable:
    name: str
    type: Type
    size: int

    def get_multi_attr_str(self) -> MultiAttrString:
        pairs = self.type.get_multi_attr_str_pairs()

        # Hack to add space between type and variable name (if needed)
        pairs.append((
            ('' if pairs[-1][0][-1] == ' ' else ' ') + self.name,
            [Colors.VARIABLE.color()]
        ))

        return MultiAttrString(pairs)

    def __str__(self):
        return f'{self.type} {self.name}'
