cmake_minimum_required(VERSION 3.17)
project(rlottie-python)

add_subdirectory(rlottie)

# Install the module
if (WIN32)
    install(TARGETS rlottie
            EXCLUDE_FROM_ALL
            RUNTIME DESTINATION ${PY_BUILD_CMAKE_MODULE_NAME}
            COMPONENT python_module)
else()
    install(TARGETS rlottie
            EXCLUDE_FROM_ALL
            LIBRARY DESTINATION ${PY_BUILD_CMAKE_MODULE_NAME}
            COMPONENT python_module)
endif()