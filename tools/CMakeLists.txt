find_package(fmt REQUIRED)

set(CMAKE_CXX_FLAGS "-O2 -Wall -Wextra --std=c++20")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/../)

add_executable(cmdsum cmdsum.cpp)
add_executable(discript discript.cpp)
add_executable(mdiff mdiff.cpp)
add_executable(passmaker passmaker.cpp)

target_link_libraries(cmdsum PRIVATE fmt::fmt)
target_link_libraries(discript PRIVATE fmt::fmt)
target_link_libraries(mdiff PRIVATE fmt::fmt)
target_link_libraries(passmaker PRIVATE fmt::fmt)

