# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set environment variables to avoid prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install any required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3.10-venv \
    curl \
    git \
    openjdk-11-jdk \
    python3-tk \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libkrb5-dev \
    libpq-dev \
    rpm \
    zip \
    # Any additional tools you need
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Set the working directory inside the container
WORKDIR /experiment

# Create a permanent venv with all pymop dependencies
RUN pip3 install --upgrade pip && \
    # Clone and prepare mop-with-dynapt
    git clone https://github.com/allrob23/pymop-artifacts-rv.git /opt/pymop-artifacts-rv && \
    cd /opt/pymop-artifacts-rv/pymop && \ 
    # Install pymop and its dependencies
    pip3 install .  && \
    # Create a requirements file for quick reinstall
    pip3 freeze > /opt/pymop_requirements.txt

# Copy your application code into the container
COPY ./src /experiment/src


# Set ENTRYPOINT to ensure passed arguments are treated as script parameters

RUN chmod +x src/run-project.sh
ENTRYPOINT ["src/run-project.sh"]