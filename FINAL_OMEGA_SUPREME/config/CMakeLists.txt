# OMEGA_X CMakeLists.txt
# Comprehensive build system for OMEGA_X Cyber Exploitation Framework

cmake_minimum_required(VERSION 3.20)
project(OMEGA_X VERSION 2.0.0
        DESCRIPTION "OMEGA_X - Ultimate AI-Driven Cyber Exploitation Framework"
        LANGUAGES C CXX)

# Set C/C++ standards
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Build options
option(OMEGA_X_BUILD_TESTS "Build OMEGA_X tests" OFF)
option(OMEGA_X_BUILD_DOCS "Build OMEGA_X documentation" OFF)
option(OMEGA_X_BUILD_EXAMPLES "Build OMEGA_X examples" OFF)
option(OMEGA_X_ENABLE_CUDA "Enable CUDA support for AI modules" OFF)
option(OMEGA_X_STEALTH_MODE "Enable stealth compilation mode" ON)

# Platform detection
if(WIN32)
    set(OMEGA_X_PLATFORM "windows")
    add_definitions(-DOMEGA_X_WINDOWS)
elseif(UNIX AND NOT APPLE)
    set(OMEGA_X_PLATFORM "linux")
    add_definitions(-DOMEGA_X_LINUX)
elseif(APPLE)
    set(OMEGA_X_PLATFORM "macos")
    add_definitions(-DOMEGA_X_MACOS)
else()
    set(OMEGA_X_PLATFORM "unknown")
endif()

# Compiler flags
if(MSVC)
    # MSVC specific flags
    add_compile_options(/W4 /WX- /permissive-)
    if(OMEGA_X_STEALTH_MODE)
        add_compile_options(/Ob2 /Oi /Ot /GL)
        add_link_options(/LTCG /OPT:REF /OPT:ICF)
    endif()
else()
    # GCC/Clang flags
    add_compile_options(-Wall -Wextra -Wpedantic)
    if(OMEGA_X_STEALTH_MODE)
        add_compile_options(-O3 -flto -fvisibility=hidden -fdata-sections -ffunction-sections)
        add_link_options(-Wl,--gc-sections -Wl,--strip-all)
    else()
        add_compile_options(-O2 -g)
    endif()
endif()

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_BINARY_DIR}/include
)

# Find required packages
find_package(PkgConfig REQUIRED)
find_package(Threads REQUIRED)

# Optional CUDA support
if(OMEGA_X_ENABLE_CUDA)
    find_package(CUDA REQUIRED)
    if(CUDA_FOUND)
        add_definitions(-DOMEGA_X_CUDA_ENABLED)
        include_directories(${CUDA_INCLUDE_DIRS})
    endif()
endif()

# Core OMEGA_X library
add_library(omega_x_core STATIC
    src/core/omega_x_core.c
    src/core/crypto_engine.c
    src/core/network_engine.c
    src/core/persistence_engine.c
    src/core/module_loader.c
)

target_link_libraries(omega_x_core
    Threads::Threads
    ${CMAKE_DL_LIBS}
)

# Attack modules library
add_library(omega_x_attacks STATIC
    src/attacks/arp_poisoning.c
    src/attacks/network_exploitation.c
    src/attacks/financial_attacks.c
    src/attacks/command_injection.c
    src/attacks/wireless_attacks.c
)

target_link_libraries(omega_x_attacks
    omega_x_core
)

# Hardware interaction library
add_library(omega_x_hardware STATIC
    src/hardware/nfc_controller.c
    src/hardware/usb_hid.c
    src/hardware/camera_control.c
    src/hardware/smart_card.c
)

target_link_libraries(omega_x_hardware
    omega_x_core
)

# AI/ML library
add_library(omega_x_ai STATIC
    src/ai/financial_predictor.c
    src/ai/behavior_analyzer.c
    src/ai/threat_detector.c
)

target_link_libraries(omega_x_ai
    omega_x_core
)

# Main OMEGA_X executable
add_executable(omega_x
    src/main.c
    src/cli_interface.c
    src/config_parser.c
)

target_link_libraries(omega_x
    omega_x_core
    omega_x_attacks
    omega_x_hardware
    omega_x_ai
)

# Python extension module (for Python integration)
find_package(Python3 COMPONENTS Interpreter Development)
if(Python3_FOUND)
    Python3_add_library(omega_x_python MODULE
        src/python_bindings/omega_x_module.c
        src/python_bindings/py_attack_wrappers.c
    )

    target_link_libraries(omega_x_python
        omega_x_core
        omega_x_attacks
        Python3::Python
    )

    set_target_properties(omega_x_python PROPERTIES
        PREFIX ""
        OUTPUT_NAME "omega_x"
    )
endif()

# Flipper Zero integration (if available)
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/../flipperzero-firmware")
    set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/../flipperzero-firmware/toolchain/x86_64-windows.cmake")

    add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/../flipperzero-firmware" flipperzero-firmware)

    add_flipperzero_app(omega_ploutus_app
        SOURCES omega_ploutus_app.c
        APP_MANIFEST application.fam
    )
endif()

# Test suite
if(OMEGA_X_BUILD_TESTS)
    enable_testing()
    find_package(GTest REQUIRED)

    add_executable(omega_x_tests
        tests/test_core.cpp
        tests/test_attacks.cpp
        tests/test_hardware.cpp
        tests/test_ai.cpp
    )

    target_link_libraries(omega_x_tests
        omega_x_core
        omega_x_attacks
        omega_x_hardware
        omega_x_ai
        GTest::GTest
        GTest::Main
    )

    add_test(NAME omega_x_unit_tests COMMAND omega_x_tests)
endif()

# Documentation
if(OMEGA_X_BUILD_DOCS)
    find_package(Doxygen REQUIRED)

    set(DOXYGEN_PROJECT_NAME "OMEGA_X")
    set(DOXYGEN_PROJECT_VERSION ${PROJECT_VERSION})
    set(DOXYGEN_PROJECT_DESCRIPTION "Ultimate AI-Driven Cyber Exploitation Framework")
    set(DOXYGEN_INPUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/include)
    set(DOXYGEN_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/docs)
    set(DOXYGEN_GENERATE_HTML YES)
    set(DOXYGEN_GENERATE_LATEX NO)

    doxygen_add_docs(omega_x_docs
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        COMMENT "Generate OMEGA_X documentation"
    )
endif()

# Examples
if(OMEGA_X_BUILD_EXAMPLES)
    add_executable(arp_poisoning_example examples/arp_poisoning_example.c)
    target_link_libraries(arp_poisoning_example omega_x_attacks)

    add_executable(financial_attack_example examples/financial_attack_example.c)
    target_link_libraries(financial_attack_example omega_x_ai)
endif()

# Installation
install(TARGETS omega_x
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY include/
    DESTINATION include/omega_x
    FILES_MATCHING PATTERN "*.h"
)

install(FILES requirements.txt
    DESTINATION share/omega_x
)

# Package configuration
include(CMakePackageConfigHelpers)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/OMEGA_XConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/OMEGA_XConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/OMEGA_XConfig.cmake"
    INSTALL_DESTINATION lib/cmake/OMEGA_X
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/OMEGA_XConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/OMEGA_XConfigVersion.cmake"
    DESTINATION lib/cmake/OMEGA_X
)

# Print build summary
message(STATUS "OMEGA_X Build Configuration:")
message(STATUS "  Platform: ${OMEGA_X_PLATFORM}")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  Build Tests: ${OMEGA_X_BUILD_TESTS}")
message(STATUS "  Build Docs: ${OMEGA_X_BUILD_DOCS}")
message(STATUS "  Build Examples: ${OMEGA_X_BUILD_EXAMPLES}")
message(STATUS "  CUDA Support: ${OMEGA_X_ENABLE_CUDA}")
message(STATUS "  Stealth Mode: ${OMEGA_X_STEALTH_MODE}")
message(STATUS "")
message(STATUS "Ready to build OMEGA_X - The Ultimate Cyber Weapon!")
message(STATUS "Run 'cmake --build .' to compile")
