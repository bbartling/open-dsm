# SETUP
# $ sudo docker build -t bacnet-server .
# $ sudo docker run --network="host" bacnet-server

# Use an official Python runtime based on Ubuntu as a parent image
FROM python:3.10-slim-buster

# Set environment variables to reduce Python output during installations
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install any needed packages using apt-get
RUN apt-get update && apt-get install -y \
    build-essential \
    libblas-dev \
    liblapack-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/* 

# Copy requirements.txt from your current directory and install Python packages
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code from the current directory into the container
COPY bacnet_server.py bacnet_server.py

# Command to run your application
CMD ["python", "bacnet_server.py"]
