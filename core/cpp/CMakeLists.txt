cmake_minimum_required(VERSION 3.12)
project(MatchingEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find pybind11
find_package(pybind11 REQUIRED)

# Source files
set(SOURCES
    matching_engine.cpp
    bindings.cpp
)

# Create Python module
pybind11_add_module(matching_engine_core ${SOURCES})

# Include directories
target_include_directories(matching_engine_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Compiler options for optimization
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    target_compile_options(matching_engine_core PRIVATE -O3 -march=native)
endif()

# Installation
install(TARGETS matching_engine_core DESTINATION .)
