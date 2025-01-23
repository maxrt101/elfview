from elfview.data import File, CompilationUnit, Section, Symbol, Function, Variable, Type, ResolvedType
from elfview.util.curses import Position
from elfview.util.hexdump import hexdump_lines
from elfview.util.str import timestamp_to_str
from elfview import config
from typing import Any
import lief
import os


# TODO: Update to support config feature


def get_type_name_raw(obj) -> str:
    if hasattr(obj, 'type') and obj.type:
        if obj.type.kind == obj.type.KIND.POINTER:
            return get_type_name_raw(obj.type) + '*'
        elif obj.type.name:
            return obj.type.name
        else:
            return get_type_name_raw(obj.type)
    elif hasattr(obj, 'underlying_type') and obj.underlying_type:
        if obj.underlying_type.kind == obj.underlying_type.KIND.POINTER:
            return get_type_name_raw(obj.underlying_type) + '*'
        elif obj.underlying_type.name:
            return obj.underlying_type.name
        else:
            return get_type_name_raw(obj.underlying_type)
    return '<none>'


def get_type_name(obj) -> Type:
    return ResolvedType(get_type_name_raw(obj) + ' ')


def parse(filepath: str, dimensions: Position) -> tuple[File, Any]:
    with open(filepath, 'rb') as f:
        file_contents = list(f.read())

    file_hexdump = hexdump_lines(file_contents, dimensions.x // config.HEXDUMP_WIDTH_TO_BYTE_SIZE_COEFFICIENT)

    elf = lief.parse(filepath)

    sections = list()
    for section in elf.sections:
        sections.append(Section(
            name=section.name,
            type_name=section.type.name,
            addr=0,  # FIXME: How to get address
            offset=section.offset,
            size=section.size,
            flags=section.flags,
            align=section.alignment,
            hexdump=hexdump_lines(section.content.tolist(), dimensions.x // (config.HEXDUMP_WIDTH_TO_BYTE_SIZE_COEFFICIENT * 2))
        ))

    compilation_units = dict()
    for cu in elf.debug_info.compilation_units:
        if cu.name not in compilation_units:
            compilation_units[cu.name] = CompilationUnit(cu.name, list(), list(), 0, 0)

        for fn in cu.functions:
            compilation_units[cu.name].functions.append(Function(
                name=fn.name,
                return_type=get_type_name(fn) if fn.type else ResolvedType('void '),
                args=[(get_type_name(p) if p.type else ResolvedType('void '), p.name) for p in fn.parameters],
                size=fn.size
            ))
            compilation_units[cu.name].functions_size += fn.size

        for var in cu.variables:
            # TODO: Check conditions
            if var.scope.type == var.scope.TYPE.COMPILATION_UNIT and var.scope.name == cu.name and var.address is not None:
                compilation_units[cu.name].variables.append(Variable(
                    name=var.name,
                    type=get_type_name(var),
                    size=var.size
                ))
                compilation_units[cu.name].variables_size += var.size

    for name in compilation_units:
        compilation_units[name].functions = sorted(compilation_units[name].functions, key=lambda x: x.size, reverse=True)
        compilation_units[name].variables = sorted(compilation_units[name].variables, key=lambda x: x.size, reverse=True)

    symbols = list()
    for symbol in elf.symbols:
        symbols.append(Symbol(
            name=symbol.name,
            type_name=symbol.type.name,
            value=symbol.value,
            size=symbol.size,
            binding=symbol.binding.name,
            visibility=symbol.visibility.name
        ))

    return (File(
        path=filepath,
        name=os.path.basename(filepath),
        size=os.path.getsize(filepath),
        created=timestamp_to_str(os.path.getctime(filepath)),
        modified=timestamp_to_str(os.path.getmtime(filepath)),
        accessed=timestamp_to_str(os.path.getatime(filepath)),
        # TODO: stat() (access rights, disk, inode, etc)
        file_type=elf.header.file_type.name,
        machine=elf.header.machine_type.name,
        abi=elf.header.identity_os_abi.name,
        flags=[f.name for f in elf.header.flags_list],
        entrypoint=(elf.header.entrypoint, ", ".join([f.name for f in elf.functions if f.address == elf.header.entrypoint])),
        compilation_units=compilation_units,
        sections=sections,
        symbols=symbols,
        hexdump=file_hexdump
    ), elf)
