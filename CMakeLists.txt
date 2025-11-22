cmake_minimum_required(VERSION 3.28)
project(subgraph-isomorphism)

set(CMAKE_CXX_STANDARD 23)

set(SOURCES src/main.cpp
)

add_executable(subgraph-isomorphism ${SOURCES} "src/ApproximationAlgorithm.cpp")

target_include_directories(${PROJECT_NAME}
        PRIVATE
        ${PROJECT_SOURCE_DIR}/include
)