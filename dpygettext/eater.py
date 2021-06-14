# dpygettext is a fork of pygettext 1.5, taken from Python 3.10a5,
# by uKaigo.
# ----------------------------------------------------------------------
# Copyright(c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021
# Python Software Foundation; All Rights Reserved
from __future__ import print_function
import sys
import ast
import tokenize
import time
import re
from inspect import cleandoc

import polib

from . import __version__ as version
from .utils import is_literal_string, safe_eval


class TokenEater:
    def __init__(self, options):
        self.__options = options
        self.__state = self.__waiting
        self.__data = []
        self.__lineno = -1
        self.__fresh_module = True
        self.__cur_infile = None
        self.__cur_outfile = None
        self.__enclosure_count = 0
        self.__pot_files = {}
        self.__comment = ()  # (string, lineno)

    def __call__(self, ttype, tstring, start, end, line):
        self.__state(ttype, tstring, start[0])

    @property
    def __cur_potfile(self):
        return self.__pot_files.get(self.__cur_outfile)

    def __waiting(self, ttype, tstring, lineno):
        opts = self.__options
        # Do docstring extractions, if enabled
        if opts.docstrings:
            # Module docstring?
            if self.__fresh_module:
                if ttype == tokenize.STRING and is_literal_string(tstring):
                    self.__add_entry(
                        safe_eval(tstring), lineno, is_docstring=True
                    )
                    self.__fresh_module = False
                elif ttype not in (
                    tokenize.ENCODING,
                    tokenize.COMMENT,
                    tokenize.NL,
                ):
                    self.__fresh_module = False
                return

            # Class or func/method docstring?
            if ttype == tokenize.NAME and tstring in ('class', 'def'):
                self.__state = self.__suite_seen
                return

        if opts.cmd_docstrings:
            if ttype == tokenize.OP and tstring == '@':
                self.__state = self.__decorator_seen
                return
            elif ttype == tokenize.NAME and tstring == 'class':
                self.__state = self.__class_seen
                return

        if ttype == tokenize.NAME and tstring in opts.keywords:
            self.__state = self.__keyword_seen
            return

        if ttype == tokenize.COMMENT:
            comment = tstring[1:].strip().split(' ')
            if comment[0].rstrip(':') in opts.c_keywords:
                self.__comment = (' '.join(comment[1:]), lineno)

        if ttype == tokenize.STRING:
            maybe_fstring = ast.parse(tstring, mode='eval').body
            if not isinstance(maybe_fstring, ast.JoinedStr):
                return

            for value in filter(
                lambda node: isinstance(node, ast.FormattedValue),
                maybe_fstring.values,
            ):
                for call in filter(
                    lambda node: isinstance(node, ast.Call), ast.walk(value)
                ):
                    func = call.func
                    if isinstance(func, ast.Name):
                        func_name = func.id
                    elif isinstance(func, ast.Attribute):
                        func_name = func.attr
                    else:
                        continue

                    if func_name not in opts.keywords:
                        continue
                    if len(call.args) != 1 and not opts.multiple_args:
                        print(
                            (
                                '*** %(file)s:%(lineno)s: Seen unexpected amount of'
                                ' positional arguments in gettext call: %(source_segment)s'
                            )
                            % {
                                'source_segment': ast.get_source_segment(
                                    tstring, call
                                )
                                or tstring,
                                'file': self.__cur_infile,
                                'lineno': lineno,
                            },
                            file=sys.stderr,
                        )
                        continue
                    if call.keywords and not opts.multiple_args:
                        print(
                            (
                                '*** %(file)s:%(lineno)s: Seen unexpected keyword arguments'
                                ' in gettext call: %(source_segment)s'
                            )
                            % {
                                'source_segment': ast.get_source_segment(
                                    tstring, call
                                )
                                or tstring,
                                'file': self.__cur_infile,
                                'lineno': lineno,
                            },
                            file=sys.stderr,
                        )
                        continue
                    arg = call.args[0]
                    if not isinstance(arg, ast.Constant):
                        print(
                            (
                                '*** %(file)s:%(lineno)s: Seen unexpected argument type'
                                ' in gettext call: %(source_segment)s'
                            )
                            % {
                                'source_segment': ast.get_source_segment(
                                    tstring, call
                                )
                                or tstring,
                                'file': self.__cur_infile,
                                'lineno': lineno,
                            },
                            file=sys.stderr,
                        )
                        continue
                    if isinstance(arg.value, str):
                        self.__add_entry(arg.value, lineno)

    def __decorator_seen(self, ttype, tstring, lineno):
        if ttype == tokenize.NAME and tstring in ('command', 'group'):
            self.__state = self.__suite_seen
        elif ttype == tokenize.NEWLINE:
            self.__state = self.__waiting

    def __class_seen(self, ttype, tstring, lineno):
        if self.__enclosure_count == 1:
            if ttype == tokenize.NAME and tstring == 'Cog':
                self.__state = self.__suite_seen
                return

        if ttype == tokenize.OP:
            if tstring == ':' and self.__enclosure_count == 0:
                # We see a colon and we're not in an enclosure: end of def/class
                self.__state = self.__waiting
            elif tstring in '([{':
                self.__enclosure_count += 1
            elif tstring in ')]}':
                self.__enclosure_count -= 1

    def __suite_seen(self, ttype, tstring, lineno):
        # Skip over any enclosure pairs until we see the colon
        if ttype == tokenize.OP:
            if tstring == ':' and self.__enclosure_count == 0:
                # We see a colon and we're not in an enclosure: end of def/class
                self.__state = self.__suite_docstring
            elif tstring in '([{':
                self.__enclosure_count += 1
            elif tstring in ')]}':
                self.__enclosure_count -= 1

    def __suite_docstring(self, ttype, tstring, lineno):
        # Ignore any intervening noise
        if ttype == tokenize.STRING and is_literal_string(tstring):
            self.__add_entry(
                cleandoc(safe_eval(tstring)), lineno, is_docstring=True
            )
            self.__state = self.__waiting
        elif ttype not in (
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.COMMENT,
        ):
            # There was no class docstring
            self.__state = self.__waiting

    def __keyword_seen(self, ttype, tstring, lineno):
        if ttype == tokenize.OP and tstring == '(':
            self.__data = []
            self.__lineno = lineno
            self.__state = self.__open_seen
        else:
            self.__state = self.__waiting

    def __open_seen(self, ttype, tstring, lineno):
        delimiter = ')'
        if self.__options.multiple_args:
            delimiter += ','
        if ttype == tokenize.OP and tstring in delimiter:
            # We've seen the last of the translatable strings.  Record the
            # line number of the first line of the strings and update the list
            # of messages seen.  Reset state for the next batch.  If there
            # were no strings inside _(), then just ignore this entry.
            if self.__data:
                to_add = ''.join(self.__data)
                self.__add_entry(to_add, is_brace=re.search('\{.+\}', to_add))
            self.__state = self.__waiting

        elif ttype == tokenize.STRING and is_literal_string(tstring):
            self.__data.append(safe_eval(tstring))

        elif ttype not in [
            tokenize.COMMENT,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.NEWLINE,
            tokenize.NL,
        ]:
            # warn if we see anything else than STRING or whitespace
            print(
                '*** %(file)s:%(lineno)s: Seen unexpected token "%(token)s"'
                % {
                    'token': tstring,
                    'file': self.__cur_infile,
                    'lineno': self.__lineno,
                },
                file=sys.stderr,
            )
            self.__state = self.__waiting

    def __add_entry(
        self, msg, lineno=None, is_docstring=False, is_brace=False
    ):
        if lineno is None:
            lineno = self.__lineno

        entry = next(
            (entry for entry in self.__cur_potfile if entry.msgid == msg), None
        )

        occurrence = (str(self.__cur_infile), lineno)

        t_comment = None
        if self.__comment:
            if self.__comment[1] != lineno - 1:
                self.__comment = ()
            else:
                t_comment = self.__comment[0]

        flags = []
        if is_docstring:
            flags.append('docstring')
        if is_brace:
            flags.append('python-brace-format')

        if entry is None:
            if self.__options.no_location:
                occurrences = None
            else:
                occurrences = [occurrence]

            self.__cur_potfile.append(
                polib.POEntry(
                    msgid=msg,
                    tcomment=t_comment,
                    occurrences=occurrences,
                    flags=flags,
                )
            )
        elif not self.__options.no_location:
            entry.occurrences.append(occurrence)
            entry.occurrences.sort()

    def set_cur_file(self, path):
        opts = self.__options

        self.__cur_infile = path
        self.__fresh_module = True
        name = opts.output_file

        if opts.relative:
            name = '.'.join(path.name.rsplit('.')[:-1]) + '.pot'

        self.__cur_outfile = opts.output_dir / name

        if self.__cur_outfile not in self.__pot_files:
            self.__pot_files[self.__cur_outfile] = cur_potfile = polib.POFile()
            cur_potfile.metadata = {
                'Project-Id-Version': 'PACKAGE VERSION',
                'POT-Creation-Date': time.strftime('%Y-%m-%d %H:%M%z'),
                'PO-Revision-Date': 'YEAR-MO-DA HO:MI+ZONE',
                'Last-Translator': 'FULL NAME <EMAIL@ADDRESS>',
                'Language-Team': 'LANGUAGE <LL@li.org>',
                'MIME-Version': '1.0',
                'Content-Type': 'text/plain; charset=UTF-8',
                'Content-Transfer-Encoding': '8bit',
                'Generated-By': 'dpygettext %s' % version,
            }

    def write(self):
        for outfile, potfile in self.__pot_files.items():
            outfile.parent.mkdir(parents=True, exist_ok=True)
            if not self.__options.no_location:
                potfile.sort(key=lambda e: e.occurrences[0])
            if self.__options.omit_empty and not potfile:
                continue
            if outfile.name == '-':
                print(getattr(potfile, '__unicode__')())
            else:
                potfile.save(str(outfile))
