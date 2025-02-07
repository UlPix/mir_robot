cd docker/
docker compose up -d --build

sudo docker exec -it ros2-humble-gazebo-fortress /bin/bash -c "source /ws/mir_robot/install/setup.bash; ros2 launch mir_gazebo mir_gazebo_launch.py"
