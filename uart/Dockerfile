FROM nvcr.io/nvidia/l4t-base:r32.5.0 AS base

ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get install -y python3-pip socat

# Install Python packages
RUN pip3 install pyserial paho-mqtt

# Copy the service code to /opt
COPY uart/service.py uart/test_streamer.py /opt

# Set the working directory
WORKDIR /opt

# Set the default command to run the service
CMD ["python3", "service.py"]