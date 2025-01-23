from elfview.data import File, CompilationUnit, Section, Symbol, Function, Variable, Type, ModularType, ResolvedType
from elfview.util.curses import Position, get_stdscr
from elfview.util.str import timestamp_to_str, is_printable, format_escape_codes
from elfview.util.hexdump import hexdump
from elfview.util.logo import LOGO
from elfview.ui import ScrollableBuffer
from elfview import config
from elftools.dwarf.datatype_cpp import describe_cpp_datatype
from elftools.elf.sections import SymbolTableSection
from elftools.elf.elffile import ELFFile
from typing import Any
import curses
import os


# Use elftools.dwarf.datatype_cpp.describe_cpp_datatype for getting human-readable datatype string
# If set to False, will use resolve_type_name
# describe_cpp_datatype fails if type contains 'volatile', but parses C++ references and namespaces
# resolve_type_name returns ModularType which can be pretty-printed using different colors (see config.ColorMap.TYPE_*)
USE_ELFTOOLS_DESCRIBE_CPP_TYPE = False

# Prints initialization logs to curses window (stdscr) while loading and processing ELF
PRINT_INIT_LOGS_TO_CURSES = True

# Prints long line of '=' followed by CU name that is currently in processing, useful for debugging
PRINT_CU_NAME_FOR_EACH_CU = False

# Prints debug info for each variable that is parsed
VERBOSE_VARIABLE_PARSING = False


# For logs turned on with PRINT_LOGS_TO_CURSES
logs = ScrollableBuffer(Position(curses.LINES, curses.COLS))


# Update logs onto the screen
def logs_update():
    get_stdscr().clear()
    logs.render(get_stdscr())
    get_stdscr().refresh()


# Add line to logs and update screen, if PRINT_LOGS_TO_CURSES is on
def logs_print(line):
    if PRINT_INIT_LOGS_TO_CURSES:
        logs.add_line(line)
        logs_update()
        if config.DEBUG:
            get_stdscr().getch()


def get_size_from_pc(die):
    low_pc = die.attributes.get('DW_AT_low_pc')
    high_pc = die.attributes.get('DW_AT_high_pc')

    if (high_pc and low_pc) and high_pc.form == 'DW_FORM_addr':
        return high_pc.value - low_pc.value
    elif high_pc:
        return high_pc.value
    else:
        return 0


def get_die_file(cu, die):
    line_program = cu.dwarfinfo.line_program_for_CU(cu)
    file_entries = line_program['file_entry']

    if decl_file_attr := die.attributes.get('DW_AT_decl_file'):
        index = decl_file_attr.value
        if 1 <= index <= len(file_entries):
            entry = file_entries[index - 1]
            return entry.name.decode('utf-8')

    return None


def is_die_in_cu(cu, die):
    if die_decl_file := get_die_file(cu, die):
        return die_decl_file in cu.get_top_DIE().get_full_path()
    return False


def resolve_attribute_value_recursive(die, chain_attr: str, target_attr: str, default: Any) -> Any:
    if target_attr in die.attributes:
        return die.attributes[target_attr].value

    if chain_attr in die.attributes:
        return resolve_attribute_value_recursive(
            die.get_DIE_from_attribute(chain_attr),
            chain_attr,
            target_attr,
            default
        )

    return default


def resolve_type_size(die) -> int:
    base_type_size = 0
    multiplier = 1
    die_type = die.get_DIE_from_attribute('DW_AT_type')
    # TODO: upper bound to prevent potential endless loop
    while True:
        if 'DW_AT_byte_size' in die_type.attributes:
            base_type_size = die_type.attributes['DW_AT_byte_size'].value
            break
        for child in die_type.iter_children():
            if child.tag == 'DW_TAG_subrange_type':
                if 'DW_AT_upper_bound' in child.attributes:
                    multiplier *= child.attributes['DW_AT_upper_bound'].value + 1
                elif 'DW_AT_count' in child.attributes:
                    multiplier *= child.attributes['DW_AT_count'].value
                # FIXME: DW_TAG_subrange_type is empty, maybe it means that it's a [0] array?
                # else:
                #     raise ValueError('Unsupported array dimensions attributes')
        if 'DW_AT_type' not in die.attributes:
            break
        die_type = die_type.get_DIE_from_attribute('DW_AT_type')

    return base_type_size * multiplier


def resolve_type_name(die) -> Type:
    tag_modifier_map = {
        'DW_TAG_const_type': 'const',
        'DW_TAG_volatile_type': 'volatile',
        'DW_TAG_pointer_type': '*',
        'DW_TAG_reference_type': '&'
    }

    modifiers = []
    dimensions = []

    type_die = die.get_DIE_from_attribute('DW_AT_type')

    while type_die.tag in ('DW_TAG_const_type', 'DW_TAG_volatile_type', 'DW_TAG_pointer_type', 'DW_TAG_reference_type'):
        modifiers.insert(0, tag_modifier_map[type_die.tag])
        if 'DW_AT_type' not in type_die.attributes:
            break
        type_die = type_die.get_DIE_from_attribute('DW_AT_type')

    for child in type_die.iter_children():
        if child.tag == 'DW_TAG_subrange_type':
            if 'DW_AT_upper_bound' in child.attributes:
                dimensions.append(child.attributes['DW_AT_upper_bound'].value + 1)
            elif 'DW_AT_count' in child.attributes:
                dimensions.append(child.attributes['DW_AT_count'].value)
            # FIXME: DW_TAG_subrange_type is empty, maybe it means that it's a [0] array?
            # else:
                # raise ValueError('Unsupported array dimensions attributes')

    type_name = resolve_attribute_value_recursive(type_die, 'DW_AT_type', 'DW_AT_name', 'void'.encode('utf-8')).decode('utf-8')

    if type_name == 'void' and type_die.tag == 'DW_TAG_structure_type':
        type_name = 'struct'

    return ModularType(
        name=type_name,
        modifiers=modifiers,
        dimensions=dimensions,
        size=resolve_type_size(die)
    )


def parse_type(die) -> Type:
    if USE_ELFTOOLS_DESCRIBE_CPP_TYPE:
        return ResolvedType(describe_cpp_datatype(die))
    else:
        return resolve_type_name(die)


# TODO:
# def parse_call_sites(die):
#     call_sites = []
#
#     if 'DW_AT_GNU_all_call_sites' in die.attributes:
#         line_program = die.cu.dwarfinfo.line_program_for_CU(die.cu)
#         ...
#
#     for child in die.iter_children():
#         if child.tag == 'DW_TAG_call_site':
#             call_target = child.attributes.get("DW_AT_call_target_name")
#
#     return call_sites


def parse_function(die) -> Function | None:
    # TODO: Check if this can be valid?
    # if 'DW_AT_external' in die.attributes and die.attributes['DW_AT_external'].value:
    # If no location or size information is present - function is not from this CU
    # TODO: Use is_die_in_cu
    if not ('DW_AT_low_pc' in die.attributes or 'DW_AT_ranges' in die.attributes) or 'DW_AT_name' not in die.attributes:
        return None

    name = die.attributes.get('DW_AT_name').value.decode('utf-8')
    ret_type = parse_type(die) if 'DW_AT_type' in die.attributes else ResolvedType('void ')
    args = []

    for child in die.iter_children():
        if child.tag == 'DW_TAG_formal_parameter' and 'DW_AT_type' in child.attributes:
            args.append((
                parse_type(child),
                child.attributes['DW_AT_name'].value.decode('utf-8')
            ))
        elif child.tag == 'DW_TAG_unspecified_parameters':
            args.append((None, '...'))

    return Function(
        name=name,
        return_type=ret_type,
        args=args,
        size=get_size_from_pc(die)
    )


def parse_variable(cu, die) -> Variable | None:
    is_in_cu = is_die_in_cu(cu, die)
    has_location = 'DW_AT_location' in die.attributes

    if 'DW_AT_specification' in die.attributes:
        die = die.get_DIE_from_attribute('DW_AT_specification')

    if not is_in_cu or not has_location or 'DW_AT_name' not in die.attributes or die.get_parent().tag != 'DW_TAG_compile_unit':
        return None

    if VERBOSE_VARIABLE_PARSING:
        print(die.attributes.get('DW_AT_name').value.decode('utf-8'))
        print(describe_cpp_datatype(die))
        print(resolve_type_name(die))
        print('\n')

    var_type = parse_type(die)

    return Variable(
        name=die.attributes.get('DW_AT_name').value.decode('utf-8'),
        type=var_type,
        size=var_type.size if var_type is ModularType else resolve_type_size(die)
    )


def parse_compilation_units(dwarf_info):
    compilation_units = dict()

    logs_print(f'Parsing Compilation Units')

    for cu in dwarf_info.iter_CUs():
        top_die = cu.get_top_DIE()
        cu_name = top_die.get_full_path()

        if cu_name not in compilation_units:
            compilation_units[cu_name] = CompilationUnit(cu_name, list(), list(), 0, 0)

        logs_print(f'Parse CU for {cu_name}')

        if PRINT_CU_NAME_FOR_EACH_CU:
            print('=' * 120)
            print(cu_name)

        for die in cu.iter_DIEs():
            if die.tag == 'DW_TAG_subprogram':
                if fn := parse_function(die):
                    compilation_units[cu_name].functions.append(fn)
                    compilation_units[cu_name].functions_size += fn.size
            elif die.tag == 'DW_TAG_variable':
                if var := parse_variable(cu, die):
                    compilation_units[cu_name].variables.append(var)
                    compilation_units[cu_name].variables_size += var.size

    for name in compilation_units:
        compilation_units[name].functions = sorted(compilation_units[name].functions, key=lambda x: x.size, reverse=True)
        compilation_units[name].variables = sorted(compilation_units[name].variables, key=lambda x: x.size, reverse=True)

    return compilation_units


def parse_sections(elf, dimensions) -> list[Section]:
    sections = list()

    logs_print('Parsing Sections')

    for section in elf.iter_sections():
        logs_print(f'Parse section {section.name}' + (
            ' (using deferred hexdump generation)' if config.DEFER_HEXDUMP_GENERATION else ''
        ))
        sections.append(Section(
            name=section.name,
            type_name=section['sh_type'].removeprefix('SHT_'),
            addr=0,
            offset=section['sh_offset'],
            size=section['sh_size'],
            flags=section['sh_flags'],
            align=section['sh_addralign'],
            hexdump=(
                section.data()
                if config.DEFER_HEXDUMP_GENERATION
                else hexdump(section.data(), dimensions.x // (config.HEXDUMP_WIDTH_TO_BYTE_SIZE_COEFFICIENT * 2))
            )
        ))
    return sections


def parse_symbols(elf):
    logs_print('Parsing Symbols')

    symtab = elf.get_section_by_name('.symtab')

    if not symtab:
        raise ValueError("No symbol table found")

    symbols = list()
    for symbol in symtab.iter_symbols():
        symbols.append(Symbol(
            name=symbol.name,
            type_name=symbol['st_info']['type'].removeprefix('STT_'),
            value=symbol['st_value'],
            size=symbol['st_size'],
            binding=symbol['st_info']['bind'].removeprefix('STB_'),
            visibility=symbol['st_other']['visibility'].removeprefix('STV_')
        ))

    return symbols


def parse_strings_sections(elf):
    logs_print(f'Parse strings from string sections')
    strings = []

    for section in elf.iter_sections():
        if section.name in ('.strtab', '.dynstr'):
            offset = 0
            for s in section.data().split(b'\x00'):
                if len(s):
                    strings.append((section['sh_addr'] + offset, s.decode('utf-8')))
                offset += len(s) + 1

    return strings


def parse_strings_bin(file_contents: bytes | list[int], min_length: int = 4):
    logs_print(f'Parse strings from whole ELF binary (min_size={min_length})')
    strings = []
    current_string, string_start = b'', None

    append_string = lambda: (
        strings.append((string_start, format_escape_codes(current_string.decode('utf-8'))))
        if string_start and len(current_string) >= min_length
        else None
    )

    for i in range(len(file_contents)):
        if is_printable(file_contents[i]):
            string_start = string_start if string_start else i
            current_string += bytes([file_contents[i]])
        elif file_contents[i] == 0x00:
            append_string()
            current_string, string_start = b'', None
        else:
            current_string, string_start = b'', None

    append_string()

    return strings


def parse_strings(elf, file_contents: bytes | list[int]):
    if config.USE_STRINGS_FROM_SECTIONS:
        return parse_strings_sections(elf)
    else:
        return parse_strings_bin(file_contents, config.DEFAULT_STRING_MIN_LENGTH)


def get_entrypoint(elf) -> tuple[int, str]:
    entry_point_addr = elf.header['e_entry']
    entry_point_name = ''
    for section in elf.iter_sections():
        if isinstance(section, SymbolTableSection):
            for symbol in section.iter_symbols():
                if symbol['st_value'] == entry_point_addr:
                    entry_point_name = symbol.name
    return entry_point_addr, entry_point_name


def parse(filepath: str, dimensions: Position) -> tuple[File, Any]:
    for line in LOGO.split('\n'):
        logs_print(line)

    logs_print(f'Start parsing ELF at {filepath}')
    logs_print(f'Read ELF contents')

    with open(filepath, 'rb') as f:
        file_contents = list(f.read())

    if config.DEFER_HEXDUMP_GENERATION:
        logs_print(f'Using DEFERRED hexdump generation')
        file_hexdump = file_contents
    else:
        logs_print(f'Create hexdump of ELF contents')
        file_hexdump = hexdump(file_contents, dimensions.x // config.HEXDUMP_WIDTH_TO_BYTE_SIZE_COEFFICIENT)

    logs_print(f'Parse ELF (elftools)')

    file = open(filepath, 'rb')
    elf = ELFFile(file)

    if not elf.has_dwarf_info():
        raise ValueError(f'No DWARF info found in {filepath}')

    dwarf_info = elf.get_dwarf_info()

    return (File(
        path=filepath,
        name=os.path.basename(filepath),
        size=os.path.getsize(filepath),
        created=timestamp_to_str(os.path.getctime(filepath)),
        modified=timestamp_to_str(os.path.getmtime(filepath)),
        accessed=timestamp_to_str(os.path.getatime(filepath)),
        # TODO: stat() (access rights, disk, inode, etc)
        file_type=elf.header['e_type'].removeprefix('ET_'),
        machine=elf.header['e_machine'].removeprefix('EM_'),
        abi=elf.header['e_ident']['EI_OSABI'],
        # TODO: parse flags
        flags=[str(elf.header['e_flags'])], # [f.name for f in elf.header.flags_list],
        entrypoint=get_entrypoint(elf),
        compilation_units=parse_compilation_units(dwarf_info),
        sections=parse_sections(elf, dimensions),
        symbols=parse_symbols(elf),
        strings=parse_strings(elf, file_contents),
        hexdump=file_hexdump
    ), elf)