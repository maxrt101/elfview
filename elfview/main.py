from elfview import config
from elfview.app import ELFViewApp
import argparse
import curses


def app_main(stdscr, args):
    for arg in args.config_overrides:
        name, value = arg.split('=')
        if hasattr(config, name):
            setattr(config, name, eval(value))
        else:
            raise KeyError(f'Config has no {name} field')

    app = ELFViewApp(
        stdscr,
        args.file,
        args.remove_file_prefixes,
        args.backend
    )

    app.run()
    app.cleanup()


def main():
    parser = argparse.ArgumentParser(
         prog='ELFView',
         description='TUI Application to look into ELF files',
         formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50)
    )

    parser.add_argument('-b', '--backend', action='store', dest='backend',
                        help='What library to use as backend (elftools or lief)')

    parser.add_argument('-r', '--remove-file-prefix', action='append', dest='remove_file_prefixes', default=[],
                        help='Removes specified file prefix from Files window (to see the actual file name)')

    parser.add_argument('-c', '--config', action='append', dest='config_overrides', default=[],
                        help='Override config variables at runtime. Example -c DEBUG=True')

    parser.add_argument('file', metavar='FILE',
                        help='ELF file to parse')

    args = parser.parse_args()
    curses.wrapper(app_main, args)


if __name__ == '__main__':
    main()

