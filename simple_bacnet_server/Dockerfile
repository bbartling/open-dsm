# Use Ubuntu 22.04 LTS as the base image
FROM ubuntu:22.04

# Maintainer info
LABEL maintainer="Ben Bartling <ben.bartling@gmail.com>"

# Set working directory in the container (you can adjust this if needed)
WORKDIR /

# Install necessary packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip build-essential libatlas-base-dev && \
    rm -rf /var/lib/apt/lists/* 

# Install pip
RUN python3 -m ensurepip --upgrade && \
    python3 -m pip install --no-cache-dir -U pip

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install Python packages from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the necessary application files (bacnet_server.py) from the root directory
COPY bacnet_server.py .

# Print the versions of installed packages
RUN pip show numpy scikit-learn bacpypes

# Command to run your application
CMD ["python3", "bacnet_server.py"]
