# dpygettext is a fork of pygettext 1.5, taken from Python 3.10a5,
# by uKaigo.
# ----------------------------------------------------------------------
# Copyright(c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021
# Python Software Foundation; All Rights Reserved

def is_literal_string(s):
    return s[0] in '\'"' or (s[0] in 'rRuU' and s[1] in '\'"')


def safe_eval(s):
    """Unwrap quotes."""
    return eval(s, {'__builtins__': {}}, {})
