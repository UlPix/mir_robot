cd docker/
docker compose up -d --build

sudo docker exec -it ros2-humble-gazebo-fortress /bin/bash -c "source /ws/mir_robot/install/setup.bash; ros2 launch mir_gazebo mir_gazebo_launch.py"
after reboot, instead of building:
docker start ros2-humble-gazebo-fortress

make sure to
xhost +local:

clean launch:
rm -rf install/ log build/ && source /opt/ros/humble/setup.bash && colcon build --packages-up-to mir_gazebo \
&& source install/setup.bash && ros2 launch mir_gazebo mir_gazebo_launch.py

ros2 launch mir_gazebo mir_gazebo_launch.py world:=$(ros2 pkg prefix mir_gazebo)/share/mir_gazebo/worlds/warehouse.sdf
