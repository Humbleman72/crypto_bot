#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File:              setup.py
# By:                Samuel Duclos
# For:               Myself
# Description:       Compile to C before running.
# Optimize:          python setup.py build_ext --inplace
# Optimize manually: 
#                    python -m cython -3 -a crypto_logger.py
#                    gcc -shared -pthread -fPIC -fwrapv -Wall -O3 -fno-strict-aliasing -mtune=native -I/opt/conda/envs/crypto_bot/include/python3.9/ -o crypto_logger.so crypto_logger.c

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import numpy

setup(
    name="crypto_logger", 
    cmdclass={'build_ext': build_ext}, 
    include_dirs = [numpy.get_include()], 
    ext_modules=cythonize(
        [
            Extension(
                name="bootstrap", 
                sources=["bootstrap.pyx"], 
                extra_compile_args=["-Os", "-fno-strict-aliasing", "-mtune=native"], 
                language="c++", 
            ), 
            Extension(
                name="crypto_logger", 
                sources=["crypto_logger.pyx"], 
                extra_compile_args=["-Os", "-fno-strict-aliasing", "-mtune=native"], 
                language="c++", 
            ), 
            Extension(
                name="crypto_trader", 
                sources=["crypto_trader.pyx"], 
                extra_compile_args=["-Os", "-fno-strict-aliasing", "-mtune=native"], 
                language="c++", 
            ), 
        ], 
        include_path=["/opt/conda/envs/crypto_bot/include/python3.9/"], 
        language_level=3, 
    ), 
)
