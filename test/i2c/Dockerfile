FROM nvcr.io/nvidia/l4t-base:r32.5.0 AS base

RUN apt-get update
RUN apt-get install -y python3-pip

# Install Python packages
RUN pip3 install paho-mqtt smbus2

# Copy the service code to /opt
COPY i2c/service.py /opt/service.py

# Set the working directory
WORKDIR /opt

# Set the default command to run the service
CMD ["python3", "service.py"]