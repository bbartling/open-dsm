# Use a base image for Raspberry Pi with Alpine Linux
# FROM arm32v6/alpine:3.14
FROM arm32v7/alpine:latest

WORKDIR /app

RUN apk --no-cache add python3 python3-dev py3-pip
RUN apk --no-cache update
RUN pip3 install bacpypes3
RUN apk --no-cache add python3 py3-scikit-learn

# Copy your Python application into the container
COPY bacnet_server.py /app/bacnet_server.py

# Expose the UDP port that the bacnet server will use
EXPOSE 47808/udp

# Start your application
CMD ["python3", "bacnet_server.py", "--debug"]
