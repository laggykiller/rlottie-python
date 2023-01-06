cmake_minimum_required(VERSION 3.3)
project(rlottie-python)
find_package(Python3 REQUIRED COMPONENTS Development)

add_subdirectory(rlottie)

# Install the module
install(TARGETS rlottie
        EXCLUDE_FROM_ALL
        LIBRARY     DESTINATION    ${LIB_INSTALL_DIR}
        ARCHIVE     DESTINATION    ${LIB_INSTALL_DIR}
        COMPONENT python_modules)