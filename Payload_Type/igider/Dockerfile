FROM itsafeaturemythic/mythic_python_base:latest

WORKDIR /Mythic/

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    curl \
    wget \
    git \
    zip \
    upx \
    wine64 \
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