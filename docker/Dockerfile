
FROM ros:humble-ros-base

ENV DISPLAY=${DISPLAY}
ENV XAUTHORITY=/tmp/.Xauthority

RUN apt-get update && apt-get install -y \
    curl \
    lsb-release gnupg git sudo
RUN sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

RUN apt-get update 
RUN apt-get install -y \
    ignition-fortress \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /ws
RUN mkdir -p /ws/mir_robot
RUN git clone https://github.com/UlPix/mir_robot.git
WORKDIR /ws/mir_robot
RUN git config --global --add safe.directory /ws/mir_robot
RUN git checkout port_gazebo

RUN vcs import < ./ros2.repos --recursive
RUN sudo apt update && rosdep update --rosdistro=humble
RUN rosdep install --from-paths . --ignore-src -r -y --rosdistro humble
RUN source /opt/ros/humble/setup.bash
RUN colcon build --packages-up-to mir_gazebo && source install/setup.bash

CMD ["bash"]
