from dataclasses import dataclass
from elfview.ui import MultiAttrString
from elfview.util.curses import Colors


class Type:
    def get_multi_attr_str_pairs(self) -> list[MultiAttrString.Pair]:
        raise TypeError('Can\'t call get_multi_attr_str_pairs om Type (call on ResolvedType or ModularType)')

    def __str__(self):
        return '<?>'


@dataclass
class ResolvedType(Type):
    name: str

    def get_multi_attr_str_pairs(self) -> list[MultiAttrString.Pair]:
        return [(self.name, [Colors.TYPE_NAME.color()])]

    def __str__(self):
        return self.name


@dataclass
class ModularType(Type):
    name: str
    modifiers: list[str]
    dimensions: list[int]
    size: int

    def get_parts(self):
        mods = self.modifiers
        parts = []

        if 'volatile' in mods:
            parts.append('volatile')
            mods.remove('volatile')

        if len(mods) and mods[0] == 'const':
            parts.append('const')
            mods = mods[1:]

        if '*' in mods:
            idx = mods.index('*')
            for i in range(0, idx):
                parts.append(mods[i])

        parts.append(self.name)

        for m in mods:
            parts.append(m)

        return parts

    def get_multi_attr_str_pairs(self) -> list[MultiAttrString.Pair]:
        part_color_map = {
            'const': [Colors.TYPE_CONST.color()],
            'volatile': [Colors.TYPE_VOLATILE.color()],
            '*': [Colors.TYPE_POINTER.color()]
        }

        pairs = []

        parts = self.get_parts()

        for part in parts:
            if part in part_color_map:
                pairs.append((part + ' ', part_color_map[part]))
            elif part == self.name:
                pairs.append((part + ' ', [Colors.TYPE_NAME.color()]))

        # Hack to remove space between type name and dimensions
        if len(self.dimensions):
            if pairs[-1][0][-1] == ' ':
                pairs[-1] = (pairs[-1][0][:-1], pairs[-1][1])

        for d in self.dimensions:
            pairs.append(('[', [Colors.DEFAULT.color()]))
            pairs.append((f'{d}', [Colors.TYPE_DIMENSIONS.color()]))
            pairs.append((']', [Colors.DEFAULT.color()]))

        return pairs

    def __str__(self):
        return ' '.join(self.get_parts()) + ''.join([f'[{d}]' for d in self.dimensions])
