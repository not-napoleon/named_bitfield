"""
Package settings for named_bitfield
"""

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='named_bitfield',
    version='0.1.0',
    description='Compact representation of fixed width numeric values',
    long_description=long_description,

    url='https://github.com/not-napoleon/named_bitfield',

    author='Mark Tozzi',
    author_email='mark.tozzi+pypi@gmail.com',
    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Utilities',

        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='bitfields bitstrings smart_ids',
    py_modules=["named_bitfield"],
    # packages=find_packages(exclude=['tests*']),
    install_requires=['six'],

    extras_require={
        'test': ['nose'],
    },

    package_data={},
    data_files=[],
    entry_points={},
)
