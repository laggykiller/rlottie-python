cmake_minimum_required(VERSION 3.3)
project(rlottie-python)
find_package(Python3 REQUIRED COMPONENTS Development)

add_subdirectory(rlottie)

# Install the module
install(TARGETS rlottie
        EXCLUDE_FROM_ALL
        LIBRARY     DESTINATION    ${PY_BUILD_CMAKE_MODULE_NAME}
        ARCHIVE     DESTINATION    ${PY_BUILD_CMAKE_MODULE_NAME}
        COMPONENT python_modules)