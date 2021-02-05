# dpygettext is a fork of pygettext 1.5, taken from Python 3.10a5,
# by uKaigo.
# ----------------------------------------------------------------------
# Copyright(c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021
# Python Software Foundation; All Rights Reserved

import tokenize
import pathlib
import argparse
import sys

from . import __version__ as version
from .eater import TokenEater

DEFAULT_KEYWORDS = ['_']


def _parse_args(args):
    parser = argparse.ArgumentParser(
        'dpygettext',
        description='pygettext (mainly) for discord.py projects.'
    )
    parser.add_argument(
        'infiles',
        metavar='INFILES',
        nargs='+',
        type=pathlib.Path,
        help='An input file or directory. When a directory is specified, strings '
             'will be extracted from all ".py" files. Can be multiple.'
    )
    parser.add_argument(
        '-o',
        '--output-file',
        metavar='FILENAME',
        default='messages.pot',
        type=pathlib.Path,
        help='The output file name. Defaults to "messages.pot". '
             'Pass "-" to write to stdout.'
    )
    parser.add_argument(
        '-p',
        '--output-dir',
        metavar='FOLDERNAME',
        default='locales',
        type=pathlib.Path,
        help='Output files will be placed in FOLDERNAME dir. Defaults '
             'to "locales".'
    )
    parser.add_argument(
        '-k',
        '--keywords',
        action='extend',
        metavar='KEYWORD',
        default=[],
        help='Add more keyword functions. Can be multiple.'
    )
    parser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help='Recurse through directories passed as input.'
    )
    parser.add_argument(
        '--no-location',
        action='store_true',
        help="Don't write location comments."
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='- dpygettext %s' % version,
        help='Print package version and exit.'
    )
    parser.add_argument(
        '-V',
        '--verbose',
        action='store_true',
        help='Print the files being processed.'
    )
    parser.add_argument(
        '-c',
        '--command-docstrings',
        action='store_true',
        dest='cmd_docstrings',
        help='Extract all cog and command docstrings. Has no effect '
             'when used with the --docstrings option. A cog is any '
             'class inheriting a "Cog" named class.'
    )
    parser.add_argument(
        '-D',
        '--docstrings',
        action='store_true',
        help='Extract all module, class, function and method docstrings.'
    )
    parser.add_argument(
        '-m',
        '--multiple-args',
        action='store_true',
        help='Allow multiple arguments. For example '
             'KEYWORD("translate {name}", name="this"). '
             "This is useful if you're using you're own gettext function."
    )
    parser.add_argument(
        '-R',
        '--relative-to-filename',
        dest='relative',
        action='store_true',
        help='Make output file name relative to INFILE name.'
    )
    return parser.parse_args(args)


def main(args=None):
    options = _parse_args(args)
    options.keywords.extend(DEFAULT_KEYWORDS)

    all_infiles = []
    for path in options.infiles:
        if path.is_dir():
            if options.recursive:
                all_infiles.extend(path.glob('**/*.py'))
            else:
                all_infiles.extend(path.glob('*.py'))
        else:
            all_infiles.append(path)

    eater = TokenEater(options)
    for path in all_infiles:
        if options.verbose:
            print('Working on %s' % path)
        eater.set_cur_file(path)
        with path.open('rb') as fp:
            try:
                tokens = tokenize.tokenize(fp.readline)
                for _token in tokens:
                    eater(*_token)
            except tokenize.TokenError as e:
                print(
                    "%s: %s, line %d, column %d"
                    % (e.args[0], path, e.args[1][0], e.args[1][1]),
                    file=sys.stderr
                )
                return 1

    eater.write()
    return 0


if __name__ == '__main__':
    sys.exit(main())
