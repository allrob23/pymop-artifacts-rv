# Base image
FROM ubuntu:22.04

# Avoid prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive

# Install system packages and Python 3.12 via Deadsnakes PPA
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common curl git wget zip rpm vim coreutils \
    build-essential libssl-dev libffi-dev libxml2-dev \
    libxslt1-dev zlib1g-dev libkrb5-dev libpq-dev gnupg && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-venv python3.12-dev python3.12-tk && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 && \
    ln -sf /usr/bin/python3.12 /usr/local/bin/python3 && \
    ln -sf /usr/local/bin/pip3.12 /usr/local/bin/pip3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install OpenJDK 20.0.2 manually (supports x86_64 and aarch64)
RUN arch=$(uname -m) && \
    case "$arch" in \
        x86_64) JAVA_TARBALL="openjdk-20.0.2_linux-x64_bin.tar.gz" ;; \
        aarch64) JAVA_TARBALL="openjdk-20.0.2_linux-aarch64_bin.tar.gz" ;; \
        *) echo "Unsupported architecture: $arch" && exit 1 ;; \
    esac && \
    wget https://download.java.net/java/GA/jdk20.0.2/6e380f22cbe7469fa75fb448bd903d8e/9/GPL/$JAVA_TARBALL && \
    mkdir -p /opt/java && \
    tar -xzf $JAVA_TARBALL -C /opt/java && \
    rm $JAVA_TARBALL

# Set Java environment variables
ENV JAVA_HOME=/opt/java/jdk-20.0.2
ENV PATH="$JAVA_HOME/bin:$PATH"

# Set working directory
WORKDIR /experiment

# Copy all scripts into the container
COPY scripts/rq4_scripts/run_experiment_rq4.sh .
COPY scripts/rq4_scripts/run_original.sh .
COPY scripts/rq4_scripts/run_pymop.sh .
COPY scripts/rq4_scripts/run_dynapyt.sh .
COPY scripts/rq4_scripts/run_dylin.sh .
COPY scripts/rq4_scripts/run_dynapyt_libs.sh .
COPY scripts/rq4_scripts/Specs_libs/ Specs_libs/
COPY Experiment_Data/projects_evaluated.csv .

# Make scripts executable
RUN chmod +x run_*.sh

# Default command when container starts
CMD ["bash"]
