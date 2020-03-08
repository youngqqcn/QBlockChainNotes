cmake_minimum_required(VERSION 2.8.3)
project(main)
add_compile_options(-std=c++11)

set(CMAKE_MODULE_PATH  ${PROJECT_SOURCE_DIR}/cmake/)

find_package(printer_install_lib REQUIRED)

if(NOT printer_install_lib_FOUND)
    message(FATAL_ERROR  "not found printer_install_lib")
endif(NOT printer_install_lib_FOUND)


include_directories(${printer_install_lib_INCLUDE_DIR})

add_executable(${PROJECT_NAME} src/main.cc)
target_link_libraries(${PROJECT_NAME}   ${printer_install_lib_LIBRARY})

