"""
Setup script for C++ matching engine Python bindings
"""
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, Extension
import pybind11

ext_modules = [
    Pybind11Extension(
        "matching_engine_core",
        [
            "matching_engine.cpp",
            "bindings.cpp",
        ],
        include_dirs=[pybind11.get_cmake_dir() + "/../../include"],
        language='c++',
        cxx_std=17,
    ),
]

setup(
    name="matching_engine_core",
    version="0.1.0",
    author="Trading Platform",
    description="C++ Matching Engine with Python bindings",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
)
