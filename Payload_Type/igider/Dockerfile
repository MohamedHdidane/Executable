FROM itsafeaturemythic/mythic_python_base:latest

WORKDIR /Mythic/

# Enable 32-bit architecture and install Wine dependencies
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        curl \
        wget \
        git \
        zip \
        upx \
        mingw-w64 \
        wine \
        wine32 \
        winetricks \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

# Configure Wine (non-interactive, headless mode)
ENV WINEARCH=win64
ENV WINEDEBUG=-all  # Disable Wine debug logs
ENV WINEPREFIX=/root/.wine
ENV DISPLAY=:0  # Dummy value to suppress GUI errors

# Install Python for Windows silently via winetricks
RUN wineboot --init && \
    winetricks -q win10 && \
    winetricks -q vcrun2019 && \
    winetricks -q corefonts && \
    wget https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe -O /tmp/python.exe && \
    wine /tmp/python.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 && \
    rm /tmp/python.exe

# Install PyInstaller in Wine's Python
RUN wine pip install pyinstaller

# Install PyInstaller in host Python (for Linux builds)
RUN pip install --no-cache-dir pyinstaller

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

CMD ["python3", "main.py"]