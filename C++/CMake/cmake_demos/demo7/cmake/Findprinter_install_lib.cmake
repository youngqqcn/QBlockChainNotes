find_path(
    printer_install_lib_INCLUDE_DIR
    NAMES  printer.h 
    PATHS "/root/mypro/cpp/cmake_demos/demo6/install/include"
)

find_library(
    printer_install_lib_LIBRARY
    NAMES  printer
    PATHS "/root/mypro/cpp/cmake_demos/demo6/install/lib"
)

IF ( printer_install_lib_INCLUDE_DIR   AND printer_install_lib_LIBRARY )
    SET( printer_install_lib_FOUND  TRUE )
ENDIF ( printer_install_lib_INCLUDE_DIR   AND printer_install_lib_LIBRARY )


IF (printer_install_lib_FOUND)
    IF(NOT printer_install_lib_FOUND_QUIETLY)
        MESSAGE(STATUS "Found printer_install_lib ${printer_install_lib_LIBRARY}")
    ENDIF(NOT printer_install_lib_FOUND_QUIETLY)
ELSE (printer_install_lib_FOUND)
    IF(NOT printer_install_lib_FOUND_REQUIRED)
        MESSAGE(FATAL_ERROR "Found printer_install_lib ${printer_install_lib_LIBRARY}")
    ENDIF(NOT printer_install_lib_FOUND_REQUIRED)
ENDIF(printer_install_lib_FOUND)