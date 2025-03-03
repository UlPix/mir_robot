
FROM ros:humble-ros-base

ENV DISPLAY=${DISPLAY}
ENV XAUTHORITY=/tmp/.Xauthority

ARG GZ_VERSION


RUN apt-get update && apt-get install -y \
    curl \
    lsb-release gnupg git sudo
RUN sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null


RUN echo "GZ_VERSION argument: $GZ_VERSION" && \
    if [ "$GZ_VERSION" = "fortress" ]; then \
        installCMD="ignition-fortress"; \
    elif [ "$GZ_VERSION" = "harmonic" ]; then \
        installCMD="gz-harmonic"; \
    else \
        echo "Invalid version"; \
        exit 1; \
    fi && \
    echo "Selected version: $installCMD" && \
    apt-get update && \
    apt-get install -y \
    ${installCMD} \
    && rm -rf /installCMD/lib/apt/lists/*
WORKDIR /ws
RUN mkdir -p /ws/mir_robot
RUN git clone https://github.com/UlPix/mir_robot.git
WORKDIR /ws/mir_robot
RUN git config --global --add safe.directory /ws/mir_robot
RUN git checkout port_gazebo

RUN vcs import < ./ros2.repos --recursive
RUN sudo apt update && rosdep update --rosdistro=humble
RUN rosdep install --from-paths . --ignore-src -r -y --rosdistro humble
WORKDIR /ws/mir_robot
RUN /bin/bash -c "source /opt/ros/humble/setup.bash; colcon build --packages-up-to mir_gazebo"


