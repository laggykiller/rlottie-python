cmake_minimum_required(VERSION 3.17)
project(rlottie-python)

if (MSVC)
    set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /MT")
    set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MTd")
elseif (LINUX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
endif()

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