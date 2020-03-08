cmake_minimum_required(VERSION 2.8.3)

project(main)


add_compile_options(-std=c++11)


set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)
include_directories(include)



add_library(printer SHARED src/printer.cc)  #生成动态库
# add_library(printer_static STATIC src/printer.cc) #生成静态库

add_executable(${PROJECT_NAME} src/main.cc)


target_link_libraries(${PROJECT_NAME} printer)  #链接动态库, 这里的printer就是line14 行的设置的库名
# target_link_libraries(${PROJECT_NAME} printer_static)  #链接库

