cmake_minimum_required(VERSION 2.8.3)

project(printer)


add_compile_options(-std=c++11)


set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)
include_directories(include)


# add_executable(printer src/main.cc  src/printer.cc)



add_library(printer SHARED src/printer.cc)

# add_library(printer_static STATIC  src/printer.cc)  #这样也可以, 但是生成的是  libprinter_static.a  和 libprinter.so


#这样就可以生成  同名静态库和 动态库   libprinter.a  和 libprinter.so 了
add_library(printer_static  STATIC  src/printer.cc)
set_target_properties(printer_static  PROPERTIES  OUTPUT_NAME "printer")