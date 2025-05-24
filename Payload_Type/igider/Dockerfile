FROM itsafeaturemythic/mythic_python_base:latest

WORKDIR /Mythic/

# Add WineHQ repository and install Wine
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    software-properties-common \
    && wget -qO - https://dl.winehq.org/wine-builds/winehq.key | apt-key add - \
    && apt-add-repository 'deb https://dl.winehq.org/wine-builds/debian/ bullseye main' \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        curl \
        git \
        zip \
        upx \
        winehq-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Initialize Wine
RUN wine64 wineboot --init

# Install PyInstaller globally
RUN pip install --no-cache-dir pyinstaller==5.13.0

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache

# Set environment variables for PyInstaller and Wine
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache
ENV WINEARCH=win64
ENV WINEPREFIX=/root/.wine

CMD ["python3", "main.py"]