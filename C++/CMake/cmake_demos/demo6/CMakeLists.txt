cmake_minimum_required(VERSION 2.8.3)
project(printer)
add_compile_options(-std=c++11)
include_directories(include)

set(CMAKE_MODULE_PATH  ${PROJECT_SOURCE_DIR}/cmake)
set(CMAKE_INSTALL_PREFIX  ${PROJECT_SOURCE_DIR}/install)
message(${CMAKE_MODULE_PATH})
message(${CMAKE_INSTALL_PREFIX})


add_library(printer STATIC  src/printer.cc)

install(FILES cmake/Findprinter.cmake  DESTINATION cmake)
install(FILES include/printer.h  DESTINATION include)
install(TARGETS printer
    ARCHIVE DESTINATION lib)
