FROM itsafeaturemythic/mythic_python_base:latest

WORKDIR /Mythic/

# First get the basic dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gnupg \
    software-properties-common \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add WineHQ repository (for newer Wine and winetricks)
RUN dpkg --add-architecture i386 && \
    wget -O- https://dl.winehq.org/wine-builds/winehq.key | apt-key add - && \
    apt-add-repository 'deb https://dl.winehq.org/wine-builds/debian/ buster main'

# Install all dependencies including Wine
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    curl \
    wget \
    git \
    zip \
    upx \
    mingw-w64 \
    winehq-stable \
    winetricks \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configure Wine (headless mode)
ENV WINEARCH=win64
ENV WINEDEBUG=-all
ENV WINEPREFIX=/root/.wine
ENV DISPLAY=:0

# Install Python for Windows silently
RUN wineboot --init && \
    wget https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe -O /tmp/python.exe && \
    wine /tmp/python.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 && \
    rm /tmp/python.exe

# Install PyInstaller in Wine's Python
RUN wine pip install pyinstaller

# Install PyInstaller in host Python
RUN pip install --no-cache-dir pyinstaller

# Create build cache directory
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

CMD ["python3", "main.py"]