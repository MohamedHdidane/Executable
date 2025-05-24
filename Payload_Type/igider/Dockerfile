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
    mingw-w64 \
    wine \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install PyInstaller globally
RUN pip install --no-cache-dir pyinstaller


# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache

# Set environment variables for PyInstaller
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache
ENV WINE_PREFIX=/root/.wine

CMD ["python3", "main.py"]