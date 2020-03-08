cmake_minimum_required(VERSION 2.8.3)

project(main)


add_compile_options(-std=c++11)


set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)
include_directories(include)



add_executable(${PROJECT_NAME} src/main.cc)


#方法一:  直接写死
set(dependlibdir  /root/mypro/cpp/cmake_demos/demo5/)
target_link_libraries(${PROJECT_NAME} ${dependlibdir}/lib/libprinter.a)  #链接外部静态库
# target_link_libraries(${PROJECT_NAME} ${dependlibdir}/lib/libprinter.so)  #链接外部动态库

