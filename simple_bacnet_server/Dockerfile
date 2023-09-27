# Use a base image for Raspberry Pi with Alpine Linux
# FROM arm32v6/alpine:3.14
FROM arm32v7/alpine:latest

WORKDIR /app

# Update package repositories and install necessary dependencies
RUN apk --no-cache update && \
    apk --no-cache add python3 py3-scikit-learn openblas freetype-dev libpng-dev && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h

# Install bacpypes3 using pip3
RUN apk --no-cache add py3-pip && \
    pip3 install bacpypes3 && \
    apk del py3-pip && \
    rm -rf /var/cache/apk/*

# Copy your Python application into the container
COPY bacnet_server.py /app/bacnet_server.py

# Expose the UDP port that the bacnet server will use
EXPOSE 47808/udp

# Start your application
CMD ["python3", "bacnet_server.py", "--debug"]
