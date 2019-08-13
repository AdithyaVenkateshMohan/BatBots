execute_process(COMMAND "/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/build/mybot_sonar/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/build/mybot_sonar/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
