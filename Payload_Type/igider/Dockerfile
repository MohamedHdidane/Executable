FROM itsafeaturemythic/mythic_python_base:latest

WORKDIR /Mythic/

# Install system dependencies (including MinGW for cross-compilation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    curl \
    wget \
    git \
    zip \
    upx \
    mingw-w64 \
    wine \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python for Windows in Wine (required for PyInstaller)
RUN winecfg && \
    wget https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe -O /tmp/python.exe && \
    wine /tmp/python.exe /quiet InstallAllUsers=1 PrependPath=1 && \
    rm /tmp/python.exe

# Install PyInstaller in Wine's Python
RUN wine pip install pyinstaller

# Install PyInstaller in host Python (for Linux builds)
RUN pip install --no-cache-dir pyinstaller

# Set Wine to Windows 10 mode (avoid compatibility issues)
RUN wine reg add 'HKEY_CURRENT_USER\Software\Wine\WineDbg' /v ShowCrashDialog /t REG_DWORD /d 0 /f

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache

# Set environment variables
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache
ENV WINEARCH=win64
ENV WINEPREFIX=/root/.wine

CMD ["python3", "main.py"]