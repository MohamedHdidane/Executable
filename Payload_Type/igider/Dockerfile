FROM itsafeaturemythic/mythic_python_base:latest

WORKDIR /Mythic/

# Install system dependencies, Wine, and winetricks
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        gnupg2 \
        software-properties-common \
        ca-certificates \
        winetricks && \
    wget -qO - https://dl.winehq.org/wine-builds/winehq.key | apt-key add - || { echo "Failed to add WineHQ key"; exit 1; } && \
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
        wine64 && \
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