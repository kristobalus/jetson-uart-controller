FROM nvcr.io/nvidia/l4t-base:r32.4.3 AS base

RUN apt-get update
RUN apt-get install -y python3-pip

# Install Python packages
RUN pip3 install pyserial paho-mqtt smbus2 tfmpi2c

# Copy the service code to /opt
COPY .. /opt/

# Set the working directory
WORKDIR /opt

# Set the default command to run the service
CMD ["python3", "service.py"]