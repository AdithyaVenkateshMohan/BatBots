#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
    DESTDIR_ARG="--root=$DESTDIR"
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/src/mybot_sonar"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/install/lib/python2.7/dist-packages:/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/build" \
    "/usr/bin/python" \
    "/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/src/mybot_sonar/setup.py" \
    build --build-base "/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/build/mybot_sonar" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/install" --install-scripts="/home/adithya/Ros_practice/DiffDriveRobot/FromScarRobot/mybot_ws/install/bin"
