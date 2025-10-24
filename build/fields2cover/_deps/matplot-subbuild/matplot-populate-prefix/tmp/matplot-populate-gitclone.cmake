
if(NOT "/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-subbuild/matplot-populate-prefix/src/matplot-populate-stamp/matplot-populate-gitinfo.txt" IS_NEWER_THAN "/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-subbuild/matplot-populate-prefix/src/matplot-populate-stamp/matplot-populate-gitclone-lastrun.txt")
  message(STATUS "Avoiding repeated git clone, stamp file is up to date: '/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-subbuild/matplot-populate-prefix/src/matplot-populate-stamp/matplot-populate-gitclone-lastrun.txt'")
  return()
endif()

execute_process(
  COMMAND ${CMAKE_COMMAND} -E rm -rf "/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-src"
  RESULT_VARIABLE error_code
  )
if(error_code)
  message(FATAL_ERROR "Failed to remove directory: '/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-src'")
endif()

# try the clone 3 times in case there is an odd git clone issue
set(error_code 1)
set(number_of_tries 0)
while(error_code AND number_of_tries LESS 3)
  execute_process(
    COMMAND "/usr/bin/git"  clone --no-checkout --config "advice.detachedHead=false" "https://github.com/alandefreitas/matplotplusplus.git" "matplot-src"
    WORKING_DIRECTORY "/home/nathan/ros2_ws/build/fields2cover/_deps"
    RESULT_VARIABLE error_code
    )
  math(EXPR number_of_tries "${number_of_tries} + 1")
endwhile()
if(number_of_tries GREATER 1)
  message(STATUS "Had to git clone more than once:
          ${number_of_tries} times.")
endif()
if(error_code)
  message(FATAL_ERROR "Failed to clone repository: 'https://github.com/alandefreitas/matplotplusplus.git'")
endif()

execute_process(
  COMMAND "/usr/bin/git"  checkout 5d01eb3695b07634a2b6642fd423740dea9b026c --
  WORKING_DIRECTORY "/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-src"
  RESULT_VARIABLE error_code
  )
if(error_code)
  message(FATAL_ERROR "Failed to checkout tag: '5d01eb3695b07634a2b6642fd423740dea9b026c'")
endif()

set(init_submodules TRUE)
if(init_submodules)
  execute_process(
    COMMAND "/usr/bin/git"  submodule update --recursive --init 
    WORKING_DIRECTORY "/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-src"
    RESULT_VARIABLE error_code
    )
endif()
if(error_code)
  message(FATAL_ERROR "Failed to update submodules in: '/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-src'")
endif()

# Complete success, update the script-last-run stamp file:
#
execute_process(
  COMMAND ${CMAKE_COMMAND} -E copy
    "/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-subbuild/matplot-populate-prefix/src/matplot-populate-stamp/matplot-populate-gitinfo.txt"
    "/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-subbuild/matplot-populate-prefix/src/matplot-populate-stamp/matplot-populate-gitclone-lastrun.txt"
  RESULT_VARIABLE error_code
  )
if(error_code)
  message(FATAL_ERROR "Failed to copy script-last-run stamp file: '/home/nathan/ros2_ws/build/fields2cover/_deps/matplot-subbuild/matplot-populate-prefix/src/matplot-populate-stamp/matplot-populate-gitclone-lastrun.txt'")
endif()

