cmake_minimum_required(VERSION 2.8.3)

project(printer)


add_compile_options(-std=c++11)


include_directories(include)


# add_executable(printer src/main.cc  src/printer.cc)

add_library(printer STATIC  src/printer.cc)