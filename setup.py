from setuptools import setup, find_packages
from re import search, M as MULTILINE


def _open(file):
    with open(file) as f:
        return f.read()


version = search(
    r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    _open('dpygettext/__init__.py'),
    MULTILINE,
).group(1)


setup(
    name='dpygettext',
    version=version,
    description='.',
    long_description=_open('README.rst'),
    keywords=['gettext', 'discord.py'],
    author='uKaigo',
    license='bsd-3-clause',
    url='https://github.com/uKaigo/dpygettext',
    project_urls={'Issues': 'https://github.com/uKaigo/dpygettext/issues'},
    packages=find_packages(),
    install_requires=_open('requirements.txt'),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License: : OSI Approved :: BSD License'
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3'
        'Programming Language :: Python :: 3.6'
        'Programming Language :: Python :: 3.7'
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={'console_scripts': ['dpygettext=dpygettext.__main__:main']},
)
