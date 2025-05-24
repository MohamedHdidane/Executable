FROM itsafeaturemythic/mythic_python_base:latest

WORKDIR /Mythic/

# Install system dependencies, Wine, and winetricks
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        gnupg2 \
        software-properties-common \
        ca-certificates && \
    # Add Debian contrib repository for winetricks
    echo "deb http://deb.debian.org/debian buster contrib" >> /etc/apt/sources.list && \
    # Fetch WineHQ key with retry mechanism
    for i in {1..3}; do \
        wget -qO - https://dl.winehq.org/wine-builds/winehq.key | apt-key add - && break || \
        { echo "Retrying WineHQ key download ($i/3)"; sleep 2; }; \
    done || { echo "Failed to add WineHQ key after 3 attempts"; exit 1; } && \
    # Add WineHQ repository dynamically
    . /etc/os-release && \
    echo "deb https://dl.winehq.org/wine-builds/${ID}/ ${VERSION_CODENAME} main" > /etc/apt/sources.list.d/winehq.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        curl \
        git \
        zip \
        upx \
        winehq-stable \
        wine64 \
        winetricks && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download Python installer for Wine
RUN wget -O /opt/python-3.9.10-amd64.exe https://www.python.org/ftp/python/3.9.10/python-3.9.10-amd64.exe && \
    chmod +x /opt/python-3.9.10-amd64.exe && \
    ls -l /opt/python-3.9.10-amd64.exe

# Initialize Wine and install Windows components
RUN wine64 wineboot --init || { echo "Wine initialization failed"; exit 1; } && \
    winetricks -q vcrun2019

# Install PyInstaller globally on host
RUN pip install --no-cache-dir pyinstaller==5.13.0

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache

# Set environment variables
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache
ENV WINEARCH=win64
ENV WINEPREFIX=/root/.wine

CMD ["python3", "main.py"]