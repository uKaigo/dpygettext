dpygettext
==========
A modified version of pygettext for `discord.py <https://github.com/rapptz/discord.py>`_ bots.

Installation
------------
::

    pip install git+https://github.com/uKaigo/dpygettext

Help
----
::

    usage: dpygettext [-h] [-o FILENAME] [-p FOLDERNAME] [-k KEYWORD] [-r]
                      [--no-location] [-v] [-V] [-c] [-D] [-m] [-R]
                      INFILES [INFILES ...]

    pygettext (mainly) for discord.py projects.

    positional arguments:
      INFILES               An input file or directory. When a directory is
                            specified, strings will be extracted from all ".py"
                            files. Can be multiple.

    optional arguments:
      -h, --help            show this help message and exit
      -o FILENAME, --output-file FILENAME
                            The output file name. Defaults to "messages.pot". Pass
                            "-" to write to stdout.
      -p FOLDERNAME, --output-dir FOLDERNAME
                            Output files will be placed in FOLDERNAME dir.
                            Defaults to "locales".
      -k KEYWORD, --keywords KEYWORD
                            Add more keyword functions. Can be multiple.
      -r, --recursive       Recurse through directories passed as input.
      --no-location         Don't write location comments.
      -v, --version         Print package version and exit.
      -V, --verbose         Print the files being processed.
      -c, --command-docstrings
                            Extract all cog and command docstrings. Has no effect
                            when used with the --docstrings option. A cog is any
                            class inheriting a "Cog" named class.
      -D, --docstrings      Extract all module, class, function and method
                            docstrings.
      -m, --multiple-args   Allow multiple arguments. For example
                            KEYWORD("translate {name}", name="this"). This is
                            useful if you're using you're own gettext function.
      -R, --relative-to-filename
                            Make output file name relative to INFILE name.


Copyright
---------
Copyright(c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 
2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021 Python Software Foundation; 
All Rights Reserved
