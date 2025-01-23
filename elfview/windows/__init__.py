from elfview.ui import Window
from .general.general import GeneralInfoPad
from .sections.section_list import SectionsListPad
from .sections.section_info import SectionInfoPad
from .files.file_list import FilesPad
from .files.fn_var import FuncsVarsPad
from .files.info import InfoPad
from .symbols.symbols import SymbolsListPad
from .strings.strings import StringListPad
from .hexdump.hexdump import HexdumpPad


def create(app: 'App') -> list[Window]:
    return [
        Window('General', app, [
            GeneralInfoPad()
        ]),
        Window('Sections', app, [
            SectionsListPad(),
            SectionInfoPad()
        ]),
        Window('Files/Functions', app, [
            FilesPad(),
            FuncsVarsPad(),
            InfoPad()
        ]),
        Window('Symbols', app, [
            SymbolsListPad()
        ]),
        Window('Strings', app, [
            StringListPad()
        ]),
        Window('Hexdump', app, [
            HexdumpPad()
        ])
    ]
